import pytest
import os

os.environ["MODEL_MOCK"] = "1"
from sqlalchemy import create_engine, text
from app.api import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_db(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("data") / "test.sqlite"
    db_url = f"sqlite:///{db_path}"

    engine = create_engine(db_url, connect_args={"check_same_thread": False})

    schema = """
    CREATE TABLE IF NOT EXISTS raw (
        id_employee INTEGER,
        age INTEGER,
        revenu_mensuel INTEGER,
        nombre_experiences_precedentes INTEGER,
        annee_experience_totale INTEGER,
        annees_dans_l_entreprise INTEGER,
        annees_dans_le_poste_actuel INTEGER,
        satisfaction_employee_environnement INTEGER,
        note_evaluation_actuelle INTEGER,
        note_evaluation_precedente INTEGER,
        niveau_hierarchique_poste INTEGER,
        satisfaction_employee_nature_travail INTEGER,
        satisfaction_employee_equipe INTEGER,
        satisfaction_employee_equilibre_pro_perso INTEGER,
        nombre_participation_pee INTEGER,
        nb_formations_suivies INTEGER,
        distance_domicile_travail INTEGER,
        niveau_education INTEGER,
        annees_depuis_la_derniere_promotion INTEGER,
        annes_sous_responsable_actuel INTEGER,
        augmentation_salaire_precedente INTEGER,
        score_evolution_carriere REAL,
        indice_evolution_salaire REAL,
        frequence_deplacement TEXT,
        salaire_cat TEXT,
        salaire_cat_eq TEXT,
        position_salaire_poste TEXT,
        position_salaire_poste_anc TEXT,
        score_carriere_cat TEXT,
        indice_evol_cat TEXT,
        statut_marital TEXT,
        domaine_etude TEXT,
        poste_departement TEXT,
        genre TEXT,
        heure_supplementaires TEXT,
        nouveau_responsable TEXT,
        attrition_num INTEGER
    );
    CREATE TABLE IF NOT EXISTS model_input (
        input_id INTEGER,
        timestamp TEXT,
        payload TEXT
    );
    CREATE TABLE IF NOT EXISTS model_output (
        output_id INTEGER,
        input_id INTEGER,
        timestamp TEXT,
        prediction TEXT,
        model_version TEXT
    );
    CREATE TABLE IF NOT EXISTS api_log (
        log_id INTEGER,
        timestamp TEXT,
        event_type TEXT,
        request_payload TEXT,
        response_payload TEXT,
        http_code INTEGER,
        user_id TEXT,
        duration_ms INTEGER,
        error_detail TEXT
    );
    """

    with engine.connect() as conn:
        for stmt in schema.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))

        # Table raw (2 employés)
        conn.execute(
            text(
                """
        INSERT INTO raw (
            id_employee, age, revenu_mensuel, nombre_experiences_precedentes,
            annee_experience_totale, annees_dans_l_entreprise, annees_dans_le_poste_actuel,
            satisfaction_employee_environnement, note_evaluation_actuelle, note_evaluation_precedente,
            niveau_hierarchique_poste, satisfaction_employee_nature_travail, satisfaction_employee_equipe,
            satisfaction_employee_equilibre_pro_perso, nombre_participation_pee, nb_formations_suivies,
            distance_domicile_travail, niveau_education, annees_depuis_la_derniere_promotion,
            annes_sous_responsable_actuel, augmentation_salaire_precedente, score_evolution_carriere,
            indice_evolution_salaire, frequence_deplacement, salaire_cat, salaire_cat_eq,
            position_salaire_poste, position_salaire_poste_anc, score_carriere_cat, indice_evol_cat,
            statut_marital, domaine_etude, poste_departement, genre, heure_supplementaires,
            nouveau_responsable, attrition_num
        ) VALUES
        (
            1, 30, 3000, 3, 7, 5, 2, 4, 5, 3, 1, 3, 4, 4, 1, 1, 10, 2, 1, 2, 1, 0.5, 0.1, 'Rare',
            'Bas', 'Bas', 'Bas', 'Moyen', 'Moyen', 'Bas', 'Bas', 'Marié', 'Sciences', 'IT', 'H', 'Non', 'Non', 0
        ),
        (
            2, 40, 4500, 5, 15, 10, 4, 5, 6, 5, 2, 4, 5, 4, 2, 2, 20, 4, 5, 4, 2, 0.7, 0.2, 'Régulier',
            'Moyen', 'Moyen', 'Haut', 'Haut', 'Haut', 'Haut', 'Célibataire', 'Eco', 'HR', 'F', 'Oui', 'Oui', 1
        )
    """
            )
        )

        # Table model_input
        conn.execute(
            text(
                """
            INSERT INTO model_input (input_id, timestamp, payload) VALUES
            (101, '2025-11-25 14:22:00', '{"id_employee": 1, "age": 30}'),
            (102, '2025-11-25 14:25:01', '{"id_employee": 2, "age": 40}')
        """
            )
        )

        # Table model_output
        conn.execute(
            text(
                """
            INSERT INTO model_output (output_id, input_id, timestamp, prediction, model_version) VALUES
            (201, 101, '2025-11-25 14:24:18', '{"prediction": "OUI"}', '1.0'),
            (202, 102, '2025-11-25 14:26:38', '{"prediction": "NON"}', '1.0')
        """
            )
        )

        # Table api_log
        conn.execute(
            text(
                """
            INSERT INTO api_log (log_id, timestamp, event_type, request_payload, response_payload,
                http_code, user_id, duration_ms, error_detail) VALUES
            (301, '2025-11-25 14:27:10', 'predict', '{"id_employee": 1}', '{"prediction": "OUI"}', 200, 'user1', 222, NULL),
            (302, '2025-11-25 14:28:01', 'predict', '{"id_employee": 2}', '{"prediction": "NON"}', 200, 'user2', 240, NULL)
        """
            )
        )

    os.environ["DBTYPE"] = "sqlite"
    os.environ["DBNAME"] = str(db_path)

    yield engine


@pytest.fixture(scope="module")
def client(test_db):
    with TestClient(app) as test_client:
        yield test_client
