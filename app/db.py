from sqlalchemy import create_engine, text

SQLITE_URL = "sqlite:///app.db"
engine = create_engine(SQLITE_URL)


def get_employee_features(employee_id):
    with engine.connect() as conn:
        query = text("SELECT * FROM employees WHERE employee_id = :id")
        result = conn.execute(query, {"id": employee_id}).fetchone()
        if result is None:
            return None
        return dict(result)
