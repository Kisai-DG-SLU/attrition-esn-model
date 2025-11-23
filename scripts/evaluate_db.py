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

# Vérification du contenu de chaque table
for table in tables:
    print(f"\n\n===== TABLE : {table.upper()} =====")
    try:
        query = f"SELECT * FROM {table} LIMIT 5;"
        df = pd.read_sql(query, engine)
        print(f"\n--- HEAD ({table}) ---")
        print(df.head())
        print(f"\n--- INFO ({table}) ---")
        print(df.info())
    except (ProgrammingError, OperationalError) as e:
        print(f"Table '{table}' non accessible ou n'existe pas : {e}")
    except Exception as e:
        print(f"Erreur inattendue sur '{table}': {e}")

# Vérification des clés primaires
query_pk = """
SELECT
    tc.table_name, 
    kcu.column_name
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
     AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema = 'public';
"""
print("\n\n=== CLÉS PRIMAIRES ===")
try:
    df_pk = pd.read_sql(query_pk, engine)
    print(df_pk)
except Exception as e:
    print(f"Erreur lors de l'inspection PK: {e}")

# Vérification des clés étrangères
query_fk = """
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
     AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
     AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public';
"""
print("\n\n=== CLÉS ÉTRANGÈRES ===")
try:
    df_fk = pd.read_sql(query_fk, engine)
    print(df_fk)
except Exception as e:
    print(f"Erreur lors de l'inspection FK: {e}")

# Vérification des index
query_idx = """
SELECT 
    tablename, 
    indexname, 
    indexdef 
FROM 
    pg_indexes 
WHERE 
    schemaname = 'public';
"""
print("\n\n=== INDEX ===")
try:
    df_idx = pd.read_sql(query_idx, engine)
    print(df_idx)
except Exception as e:
    print(f"Erreur lors de l'inspection des index: {e}")
