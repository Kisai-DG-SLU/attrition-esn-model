from fastapi import FastAPI, Query
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

# Détecte l'environnement (dev/test/prod) via la variable ENV
ENV = os.getenv("ENV", "dev")

# Charge le .env en local (ignoré en prod si pas présent)
if ENV == "dev":
    load_dotenv(".env")  # ou ".env.dev" si tu préfères

# Récupération des variables d'environnement (toujours via ENV VARS)
user = os.getenv("DB_USER_DEMO")
pwd = os.getenv("DB_PW_DEMO")
db_host = os.getenv("DB_SYS_HOST")
db_port = os.getenv("DB_SYS_PORT", "5432")
db_name = os.getenv("DB_NAME")
DB_TYPE = os.getenv("DB_TYPE", "postgresql")  # Pour switcher postgres/sqlite si besoin

# Construction dynamique de la chaîne de connexion
if DB_TYPE == "sqlite":
    DB_CONNECT = (
        f"sqlite:///{db_name}"  # db_name = chemin local vers le fichier .sqlite
    )
else:
    DB_CONNECT = f"postgresql+psycopg2://{user}:{pwd}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DB_CONNECT)

app = FastAPI(
    title="API Attrition Demo",
    description=f"Swagger FastAPI + accès BDD via SQLAlchemy [{ENV}]",
    version="1.0",
)

model_path = os.path.join(
    os.path.dirname(__file__), "..", "models", "model_pipeline.joblib"
)
model_pipeline = joblib.load(model_path)


def get_raw_employee(id_employee):
    query = text("SELECT * FROM raw WHERE id_employee = :id")
    df_emp = pd.read_sql(query, engine, params={"id": id_employee})

    if df_emp.empty:
        return None
    return df_emp.iloc[0]


def predict_core(id_employee):
    emp_row = get_raw_employee(id_employee)
    if emp_row is None:
        return {"error": "ID salarié non trouvé"}

    # Préparation de la ligne pour le modèle
    emp_features = emp_row.to_dict()
    emp_features.pop("id_employee", None)
    emp_features.pop("attrition_num", None)
    X_row = pd.DataFrame([emp_features])

    score = float(model_pipeline.predict_proba(X_row)[0][1])
    pred = "OUI" if score >= 0.55 else "NON"

    # Pipeline de preprocessing
    preprocessor = model_pipeline.named_steps["preprocessor"]
    X_processed = preprocessor.transform(X_row)
    if hasattr(preprocessor, "get_feature_names_out"):
        feature_names = preprocessor.get_feature_names_out()
    else:
        feature_names = [f"feat_{i}" for i in range(X_processed.shape[1])]
    df_processed = pd.DataFrame(X_processed, columns=feature_names)

    # SHAP pour XGBoost
    estimator = list(model_pipeline.named_steps.values())[-1]
    explainer = shap.TreeExplainer(estimator)
    shap_values = explainer(df_processed)
    shap_explanation = shap_values[0]

    plt.clf()
    shap.plots.waterfall(shap_explanation, show=False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    contribs = dict(zip(feature_names, shap_explanation.values.tolist()))
    print("Valeurs SHAP réelles :", shap_explanation.values)
    print("Contributions SHAP :", contribs)

    return {
        "prediction": pred,
        "score": score,
        "donnees_brutes": emp_row.to_dict(),
        "id_employee": id_employee,
        "shap_waterfall": contribs,
        "shap_waterfall_img": img_b64,
    }


@app.get("/predict/")
def predict(id_employee: int = Query(...)):
    return predict_core(id_employee)


class EmployeeRequest(BaseModel):
    id_employee: int


@app.post("/predict/")
def predict_post(payload: EmployeeRequest):
    return predict_core(payload.id_employee)


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0", "env": ENV}


@app.get("/employee_list")
def employee_list():
    query = "SELECT id_employee FROM raw"
    df = pd.read_sql(query, engine)
    return df["id_employee"].drop_duplicates().tolist()
