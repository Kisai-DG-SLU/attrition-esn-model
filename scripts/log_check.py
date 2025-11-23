import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv("DB_SYS_HOST")
db_port = os.getenv("DB_SYS_PORT", "5432")
db_name = os.getenv("DB_NAME")
user = os.getenv("DB_USER_ADMIN")
password = os.getenv("DB_PW_ADMIN")

engine = create_engine(
    f"postgresql+psycopg2://{user}:{password}@{db_host}:{db_port}/{db_name}"
)

tables = ["model_input", "model_output", "api_log"]

for table in tables:
    print(f"\n=== Table : {table} ===")
    try:
        # Affiche les 5 dernières entrées pour contrôle rapide
        df = pd.read_sql(
            f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 5;", engine
        )
        print(df)
        print(f"{table} : {len(df)} lignes lues.")
    except Exception as e:
        print(f"Erreur lecture {table} : {e}")
