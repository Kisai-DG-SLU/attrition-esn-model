from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import shap
from sqlalchemy import create_engine, text
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from dotenv import load_dotenv
import json
import time

# Chargement variables d'environnement
ENV = os.getenv("ENV", "dev")
if ENV == "dev":
    load_dotenv(".env")
    from psycopg2 import connect

demo_user = os.getenv("DB_USER_DEMO")
demo_pwd = os.getenv("DB_PW_DEMO")
log_user = os.getenv("DB_USER_LOG")
log_pwd = os.getenv("DB_PW_LOG")
db_host = os.getenv("DB_SYS_HOST")
db_port = os.getenv("DB_SYS_PORT", "5432")
db_name = os.getenv("DB_NAME")
DB_TYPE = os.getenv("DB_TYPE", "postgresql")

READONLY_DB = os.getenv("READONLY_DB", "0") == "1"

def get_engine(role="demo"):
    if DB_TYPE == "sqlite":
        db_connect = f"sqlite:///{db_name}"
    else:
        if role == "demo":
            db_connect = f"postgresql+psycopg2://{demo_user}:{demo_pwd}@{db_host}:{db_port}/{db_name}"
        elif role == "log":
            db_connect = f"postgresql+psycopg2://{log_user}:{log_pwd}@{db_host}:{db_port}/{db_name}"
        else:
            raise ValueError("Role must be 'demo' or 'log'")
    return create_engine(db_connect)


engine = None
engine_log = None


def set_engine_for_tests(new_engine):
    global engine, engine_log
    engine = new_engine
    engine_log = new_engine


if engine is None or engine_log is None:
    engine = get_engine(role="demo")
    engine_log = get_engine(role="log")

app = FastAPI(
    title="API Attrition Demo",
    description=f"Swagger FastAPI + accès BDD via SQLAlchemy [{ENV}]",
    version="1.0",
)

class DummyModel:
    """DummyModel pour mocker predict_proba et preprocessor."""

    class DummyPreproc:
        def transform(self, X):
            # Retourne X inchangé ou un array de bonnes dimensions
            import numpy as np

            return np.zeros((X.shape[0], 2))

        def get_feature_names_out(self):
            # Retourne des noms fictifs
            return ["dummy1", "dummy2"]

    def __init__(self):
        self.named_steps = {"preprocessor": self.DummyPreproc()}

    def predict_proba(self, X):
        import numpy as np

        # Retourne probas constantes : "OUI" et "NON"
        return np.array([[0.4, 0.6] for _ in range(len(X))])


model_path = os.path.join(
    os.path.dirname(__file__), "..", "models", "model_pipeline.joblib"
)

MODEL_MOCK = os.getenv("MODEL_MOCK", "0") == "1"

if not MODEL_MOCK:
    try:
        model_pipeline = joblib.load(model_path)
    except FileNotFoundError:
        # Fallback automatique sur le mock si réel absent...
        model_pipeline = DummyModel()
else:
    model_pipeline = DummyModel()

model_path = os.path.join(
    os.path.dirname(__file__), "..", "models", "model_pipeline.joblib"
)


def log_model_input(payload_dict):
    global engine_log

    if READONLY_DB:
        # Pas d'écriture en prod HF (SQLite RO)
        return -1

    with engine_log.begin() as conn:
        if conn.engine.dialect.name == "sqlite":
            conn.execute(
                text("INSERT INTO model_input (payload) VALUES (:payload)"),
                {"payload": json.dumps(payload_dict)},
            )
            result = conn.execute(text("SELECT last_insert_rowid()"))
            row = result.fetchone()
            return row[0] if row else None
        else:
            result = conn.execute(
                text(
                    "INSERT INTO model_input (payload) "
                    "VALUES (:payload) RETURNING input_id;"
                ),
                {"payload": json.dumps(payload_dict)},
            )
            return result.fetchone()[0]


def log_model_output(input_id, prediction, model_version=None):
    global engine_log

    if READONLY_DB:
        # Pas de log, on renvoie un ID factice
        return -1

    with engine_log.begin() as conn:
        if conn.engine.dialect.name == "sqlite":
            conn.execute(
                text(
                    "INSERT INTO model_output "
                    "(input_id, prediction, model_version) "
                    "VALUES (:input_id, :prediction, :model_version)"
                ),
                {
                    "input_id": input_id,
                    "prediction": json.dumps(prediction),
                    "model_version": model_version,
                },
            )
            result = conn.execute(text("SELECT last_insert_rowid()"))
            row = result.fetchone()
            return row[0] if row else None
        else:
            result = conn.execute(
                text(
                    "INSERT INTO model_output "
                    "(input_id, prediction, model_version) "
                    "VALUES (:input_id, :prediction, :model_version) "
                    "RETURNING output_id;"
                ),
                {
                    "input_id": input_id,
                    "prediction": json.dumps(prediction),
                    "model_version": model_version,
                },
            )
            return result.fetchone()[0]



def log_api_event(
    event_type,
    req=None,
    resp=None,
    http_code=None,
    demo_user_id=None,
    duration_ms=None,
    error=None,
):
    if READONLY_DB:
        # En prod HF, pas de trace en base
        return

    with engine_log.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO api_log (
                    event_type, request_payload, response_payload,
                    http_code, user_id, duration_ms, error_detail
                ) VALUES (
                    :event_type, :request_payload, :response_payload,
                    :http_code, :user_id, :duration_ms, :error_detail
                )
            """
            ),
            {
                "event_type": event_type,
                "request_payload": json.dumps(req) if req else None,
                "response_payload": json.dumps(resp) if resp else None,
                "http_code": http_code,
                "user_id": demo_user_id,
                "duration_ms": duration_ms,
                "error_detail": error,
            },
        )



def get_raw_employee(id_employee):
    query = text("SELECT * FROM raw WHERE id_employee = :id")
    try:
        with engine.connect() as conn:
            df_emp = pd.read_sql(query, conn, params={"id": id_employee})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données: {str(e)}")
    if df_emp.empty:
        raise HTTPException(status_code=404, detail="ID salarié non trouvé")
    return df_emp.iloc[0]


def predict_core(id_employee):
    emp_row = get_raw_employee(id_employee)
    emp_features = emp_row.to_dict()
    emp_features.pop("id_employee", None)
    emp_features.pop("attrition_num", None)
    X_row = pd.DataFrame([emp_features])

    score = float(model_pipeline.predict_proba(X_row)[0][1])
    pred = "OUI" if score >= 0.55 else "NON"

    # ----- PATCH : brancher DummyModel et normal en prod -----
    if type(model_pipeline).__name__ == "DummyModel":
        # Retourne des SHAP “fictifs”
        contribs = {"dummy1": 0.0, "dummy2": 0.0}
        img_b64 = ""
    else:
        preprocessor = model_pipeline.named_steps["preprocessor"]
        X_processed = preprocessor.transform(X_row)

        if hasattr(preprocessor, "get_feature_names_out"):
            feature_names = preprocessor.get_feature_names_out()
        else:
            feature_names = [f"feat_{i}" for i in range(X_processed.shape[1])]
        df_processed = pd.DataFrame(X_processed, columns=feature_names)
        estimator = list(model_pipeline.named_steps.values())[-1]
        import shap

        explainer = shap.TreeExplainer(estimator)
        shap_values = explainer(df_processed)
        shap_explanation = shap_values[0]
        import matplotlib.pyplot as plt
        import io
        import base64

        plt.clf()
        shap.plots.waterfall(shap_explanation, show=False)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        contribs = dict(zip(feature_names, shap_explanation.values.tolist()))

    return {
        "prediction": pred,
        "score": score,
        "donnees_brutes": emp_row.to_dict(),
        "id_employee": id_employee,
        "shap_waterfall": contribs,
        "shap_waterfall_img": img_b64,
    }


class EmployeeRequest(BaseModel):
    id_employee: int


@app.get("/predict/")
def predict(id_employee: int = Query(...)):
    start = time.time()
    try:
        input_id = log_model_input({"id_employee": id_employee})
        result = predict_core(id_employee)
        log_model_output(input_id, result, model_version="1.0")
        duration_ms = int((time.time() - start) * 1000)
        log_api_event(
            event_type="predict",
            req={"id_employee": id_employee},
            resp=result,
            http_code=200,
            demo_user_id="demo_user",
            duration_ms=duration_ms,
            error=None,
        )
        return result
    except HTTPException as e:
        duration_ms = int((time.time() - start) * 1000)
        log_api_event(
            event_type="predict_error",
            req={"id_employee": id_employee},
            resp=None,
            http_code=e.status_code,
            demo_user_id="demo_user",
            duration_ms=duration_ms,
            error=e.detail,
        )
        raise e
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        log_api_event(
            event_type="predict_error",
            req={"id_employee": id_employee},
            resp=None,
            http_code=500,
            demo_user_id="demo_user",
            duration_ms=duration_ms,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@app.post("/predict/")
def predict_post(payload: EmployeeRequest):
    return predict(id_employee=payload.id_employee)


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0", "env": ENV}


@app.get("/employee_list")
def employee_list():
    query = "SELECT id_employee FROM raw"
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
        return df["id_employee"].drop_duplicates().tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur base de données: {str(e)}")


@app.get("/log_sample/")
def log_sample(
    table: str = Query(
        ..., description="Table à inspecter: model_input/model_output/api_log"
    ),
    n: int = 3,
):
    if table not in {"model_input", "model_output", "api_log"}:
        return {"error": "Table inconnue"}

    try:
        with engine_log.connect() as conn:
            if conn.engine.dialect.name == "sqlite":
                query = f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT ?"
                params = (n,)
            else:
                query = f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT {int(n)}"
                params = {}
            df = pd.read_sql(query, conn, params=params)
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Exception in log_sample: {e}")
        return {"error": "Erreur interne du serveur"}
