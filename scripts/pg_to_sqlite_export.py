import os
import pandas as pd
import sqlite3
import psycopg2
from dotenv import load_dotenv
import json

# Charger .env
load_dotenv()
pg_creds = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_SYS_USER"),
    "password": os.getenv("DB_SYS_PASSWORD"),
    "host": os.getenv("DB_SYS_HOST"),
    "port": os.getenv("DB_SYS_PORT") or 5432,
}

# --- Connexion PostgreSQL
pg_conn = psycopg2.connect(**pg_creds)
pg_cur = pg_conn.cursor()

# --- Connexion SQLite
sqlite_path = "clone_test_db.sqlite"
sqlite_conn = sqlite3.connect(sqlite_path)

# --- Liste des tables à cloner
tables = ["raw", "model_input", "model_output", "api_log"]

for table in tables:
    print(f"Traitement {table}…")
    df = pd.read_sql(f"SELECT * FROM {table}", pg_conn)
    # Pour les colonnes JSON/object, serialize en string
    for col in df.columns:
        if df[col].dtype == "object":
            # Si la colonne contient des dict, list ou autres objets (JSON natif)
            if any(isinstance(v, (dict, list)) for v in df[col] if v is not None):
                df[col] = df[col].apply(
                    lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
                )
    df.to_sql(table, sqlite_conn, index=False, if_exists="replace")

sqlite_conn.close()
pg_cur.close()
pg_conn.close()
print(f"Base exportée dans {sqlite_path}")
