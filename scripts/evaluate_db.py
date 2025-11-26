import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
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

tables = ["raw", "model_input", "model_output", "api_log"]

# Vérification/aperçu contenu tables
for table in tables:
    print(f"\n\n===== TABLE : {table.upper()} =====")
    try:
        df = pd.read_sql(f"SELECT * FROM {table} LIMIT 5;", engine)
        print(df.head())
        print(df.info())
    except (ProgrammingError, OperationalError) as e:
        print(f"Table '{table}' non accessible ou n'existe pas : {e}")
    except Exception as e:
        print(f"Erreur inattendue avec '{table}': {e}")

# Export complet de RAW au format CSV
try:
    df_full = pd.read_sql("SELECT * FROM raw", engine)
    df_full.to_csv("raw_full.csv", index=False)
    print("Export complet terminé : raw_full.csv")
except Exception as e:
    print(f"Erreur export complet: {e}")

# Affiche les modalités de chaque colonne catégorielle
cat_cols = [
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
]
for col in cat_cols:
    try:
        vals = pd.read_sql(f"SELECT DISTINCT {col} FROM raw", engine)[col].tolist()
        print(f"{col}: {vals}")
    except Exception as e:
        print(f"Erreur valorisation {col}: {e}")
