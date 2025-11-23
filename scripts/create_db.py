# =========================
# Imports and Utilities
# =========================
import os
import psycopg2
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import re


def sanitize_column(name):
    """
    Replace spaces and special characters to make a SQL-safe column name.
    """
    name = name.strip().replace(" ", "_")
    return re.sub(r"[^a-zA-Z0-9_]", "", name)


# =========================
# Database Connection
# =========================
def get_pg_connection(role, creds, host, port):
    cred = creds[role]
    print(f"Connecting as {role} ({cred['user']})...")
    return psycopg2.connect(
        dbname=cred["dbname"],
        user=cred["user"],
        password=cred["password"],
        host=host,
        port=port,
    )


# =========================
# Data Preparation & Feature Engineering
# =========================
def add_salary_group_feature(
    df,
    group_cols=None,
    col_revenu="revenu_mensuel",
    feature_name="salary_group",
    labels=None,
):
    if labels is None:
        labels = ["Très bas", "Bas", "Moyen", "Haut"]
    if group_cols is not None:
        q1 = df.groupby(group_cols)[col_revenu].transform(lambda x: x.quantile(0.25))
        mediane = df.groupby(group_cols)[col_revenu].transform("median")
        q3 = df.groupby(group_cols)[col_revenu].transform(lambda x: x.quantile(0.75))
    else:
        q1 = pd.Series(df[col_revenu].quantile(0.25), index=df.index)
        mediane = pd.Series(df[col_revenu].median(), index=df.index)
        q3 = pd.Series(df[col_revenu].quantile(0.75), index=df.index)
    conditions = [
        df[col_revenu] < q1,
        (df[col_revenu] >= q1) & (df[col_revenu] < mediane),
        (df[col_revenu] > q3),
        (df[col_revenu] >= mediane) & (df[col_revenu] <= q3),
    ]
    df[feature_name] = np.select(conditions, labels, default="Moyen")
    return df


def create_salary_features(df, col_revenu="revenu_mensuel"):
    labels = ["Très bas", "Bas", "Moyen", "Haut"]
    df = add_salary_group_feature(
        df,
        group_cols=None,
        col_revenu=col_revenu,
        feature_name="salaire_cat",
        labels=labels,
    )
    df["salaire_cat_eq"] = pd.cut(df[col_revenu], bins=4, labels=labels)
    df = add_salary_group_feature(
        df,
        group_cols=["poste_departement"],
        col_revenu=col_revenu,
        feature_name="position_salaire_poste",
        labels=labels,
    )
    df = add_salary_group_feature(
        df,
        group_cols=["poste_departement", "annees_dans_le_poste_actuel"],
        col_revenu=col_revenu,
        feature_name="position_salaire_poste_anc",
        labels=labels,
    )
    return df


def prepare_central_data():
    df_hr = pd.read_csv("../data/raw/extrait_sirh.csv")
    df_survey = pd.read_csv("../data/raw/extrait_sondage.csv")
    df_eval = pd.read_csv("../data/raw/extrait_eval.csv")
    df_eval["eval_num"] = df_eval["eval_number"].str.extract(r"E_(\d+)").astype(int)

    df = df_hr.merge(df_eval, left_on="id_employee", right_on="eval_num").merge(
        df_survey, left_on="id_employee", right_on="code_sondage"
    )
    df["attrition_num"] = (df["a_quitte_l_entreprise"] == "Oui").astype(int)
    df["poste_departement"] = df["poste"] + "_" + df["departement"]
    df["nouveau_responsable"] = np.where(
        df["annes_sous_responsable_actuel"] == 0, "Oui", "Non"
    )
    df["augmentation_salaire_precedente"] = (
        df["augementation_salaire_precedente"]
        .str.replace("%", "", regex=False)
        .astype(int)
    )
    df["indice_evolution_salaire"] = (df["augmentation_salaire_precedente"] + 1e-6) / (
        df["annees_depuis_la_derniere_promotion"] + 1
    )
    ordre_labels = ["Très bas", "Bas", "Moyen", "Haut"]
    df["indice_evol_cat"] = pd.qcut(
        df["indice_evolution_salaire"], q=4, labels=ordre_labels
    )
    df["score_evolution_carriere"] = (
        df["indice_evolution_salaire"]
        * (1 / (df["annees_dans_l_entreprise"] + 1))
        * np.log1p(df["revenu_mensuel"])
    )
    df["score_carriere_cat"] = pd.qcut(
        df["score_evolution_carriere"], q=4, labels=ordre_labels
    )
    df = create_salary_features(df, col_revenu="revenu_mensuel")
    # Only keep relevant features for the DB
    final_features = [
        "id_employee",
        "age",
        "revenu_mensuel",
        "nombre_experiences_precedentes",
        "annee_experience_totale",
        "annees_dans_l_entreprise",
        "annees_dans_le_poste_actuel",
        "satisfaction_employee_environnement",
        "note_evaluation_actuelle",
        "note_evaluation_precedente",
        "niveau_hierarchique_poste",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
        "nombre_participation_pee",
        "nb_formations_suivies",
        "distance_domicile_travail",
        "niveau_education",
        "annees_depuis_la_derniere_promotion",
        "annes_sous_responsable_actuel",
        "augmentation_salaire_precedente",
        "score_evolution_carriere",
        "indice_evolution_salaire",
        "frequence_deplacement",
        "salaire_cat",
        "salaire_cat_eq",
        "position_salaire_poste",
        "position_salaire_poste_anc",
        "score_carriere_cat",
        "indice_evol_cat",
        "statut_marital",
        "domaine_etude",
        "poste_departement",
        "genre",
        "heure_supplementaires",
        "nouveau_responsable",
        "attrition_num",
    ]
    df = df[final_features].copy()
    # Applique le sanitize seulement ici
    df.columns = [sanitize_column(c) for c in df.columns]
    return df


# =========================
# Table Creation & Data Insertion
# =========================
def create_and_populate_table(conn, data, log_user, demo_user):
    cur = conn.cursor()
    print("Dropping and creating table 'raw'...")
    cur.execute("DROP TABLE IF EXISTS raw;")
    columns_types = []
    for col, dtype in zip(data.columns, data.dtypes):
        if dtype == "int64":
            sql_type = "INT"
        elif dtype == "float64":
            sql_type = "FLOAT"
        else:
            sql_type = "TEXT"
        columns_types.append(f"{col} {sql_type}")
    table_sql = f"CREATE TABLE raw (\n    {', '.join(columns_types)}\n);"
    cur.execute(table_sql)
    conn.commit()
    print("Table ready.")
    # Grants
    cur.execute(f"GRANT INSERT, UPDATE, SELECT ON raw TO {log_user};")
    cur.execute(f"GRANT SELECT ON raw TO {demo_user};")
    cur.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT INSERT, UPDATE, SELECT ON TABLES TO {log_user};"
    )
    cur.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {demo_user};"
    )
    print("Inserting data...")
    cols = data.columns.tolist()
    for idx, row in data.iterrows():
        placeholders = ", ".join(["%s"] * len(row))
        sql = f"INSERT INTO raw ({', '.join(cols)}) VALUES ({placeholders});"
        cur.execute(sql, tuple(row))
        if idx % 100 == 0:
            print(f"  {idx} rows inserted...")
    conn.commit()
    print(f"Inserted {len(data)} rows.")
    cur.close()


def create_exchanges_tables(conn, log_user, demo_user):
    cur = conn.cursor()

    # Table model_input
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS model_input (
            input_id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payload JSONB NOT NULL
        );
    """
    )
    cur.execute(f"GRANT INSERT, UPDATE, SELECT ON model_input TO {log_user};")
    cur.execute(f"GRANT SELECT ON model_input TO {demo_user};")
    cur.execute(
        f"GRANT USAGE, SELECT ON SEQUENCE model_input_input_id_seq TO {log_user};"
    )
    cur.execute(
        f"GRANT USAGE, SELECT ON SEQUENCE model_input_input_id_seq TO {demo_user};"
    )

    # Table model_output
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS model_output (
            output_id SERIAL PRIMARY KEY,
            input_id INTEGER REFERENCES model_input(input_id),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            prediction JSONB NOT NULL,
            model_version TEXT
        );
    """
    )
    cur.execute(f"GRANT INSERT, UPDATE, SELECT ON model_output TO {log_user};")
    cur.execute(f"GRANT SELECT ON model_output TO {demo_user};")
    cur.execute(
        f"GRANT USAGE, SELECT ON SEQUENCE model_output_output_id_seq TO {log_user};"
    )
    cur.execute(
        f"GRANT USAGE, SELECT ON SEQUENCE model_output_output_id_seq TO {demo_user};"
    )

    # Table api_log
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS api_log (
            log_id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            request_payload JSONB,
            response_payload JSONB,
            http_code INTEGER,
            user_id TEXT,
            duration_ms INTEGER,
            error_detail TEXT
        );
    """
    )
    cur.execute(f"GRANT INSERT, UPDATE, SELECT ON api_log TO {log_user};")
    cur.execute(f"GRANT SELECT ON api_log TO {demo_user};")
    cur.execute(f"GRANT USAGE, SELECT ON SEQUENCE api_log_log_id_seq TO {log_user};")
    cur.execute(f"GRANT USAGE, SELECT ON SEQUENCE api_log_log_id_seq TO {demo_user};")

    conn.commit()
    cur.close()


# =========================
# Main Routine
# =========================
def main():
    load_dotenv()
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_SYS_HOST")
    db_port = os.getenv("DB_SYS_PORT", "5432")
    creds = {
        "admin": {
            "dbname": db_name,
            "user": os.getenv("DB_USER_ADMIN"),
            "password": os.getenv("DB_PW_ADMIN"),
        },
        "log": {
            "dbname": db_name,
            "user": os.getenv("DB_USER_LOG"),
            "password": os.getenv("DB_PW_LOG"),
        },
        "demo": {
            "dbname": db_name,
            "user": os.getenv("DB_USER_DEMO"),
            "password": os.getenv("DB_PW_DEMO"),
        },
    }
    data = prepare_central_data()
    conn = get_pg_connection("admin", creds, db_host, db_port)
    create_and_populate_table(
        conn,
        data,
        log_user=os.getenv("DB_USER_LOG"),
        demo_user=os.getenv("DB_USER_DEMO"),
    )
    create_exchanges_tables(
        conn, log_user=os.getenv("DB_USER_LOG"), demo_user=os.getenv("DB_USER_DEMO")
    )
    conn.close()
    print("\nAll done! Database is populated and privileges are set.")


if __name__ == "__main__":
    main()
