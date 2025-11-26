import pytest
from fastapi import HTTPException
from app.api import (
    log_model_input,
    log_model_output,
    log_api_event,
    get_raw_employee,
    predict_core,
)

def test_log_model_input():
    """Teste l’insertion d’une entrée modèle dans la table model_input."""
    payload = {"id_employee": 1}
    input_id = log_model_input(payload)
    assert isinstance(input_id, int)
    assert input_id > 0

def test_log_model_output():
    """Teste l’insertion d’une sortie modèle dans la table model_output."""
    input_id = log_model_input({"id_employee": 1})
    prediction = {"prediction": "OUI"}
    output_id = log_model_output(input_id, prediction, model_version="1.0")
    assert isinstance(output_id, int)
    assert output_id > 0

def test_log_api_event_success():
    """Teste la journalisation d’un événement API de succès dans api_log (aucune exception attendue)."""
    log_model_input({"id_employee": 1})  # Pour générer de l’activité
    log_api_event(
        event_type="predict",
        req={"id_employee": 1},
        resp={"prediction": "OUI"},
        http_code=200,
        demo_user_id="test_user",
        duration_ms=123,
        error=None
    )

def test_log_api_event_error():
    """Teste la journalisation d’un événement d’erreur dans api_log (aucune exception attendue)."""
    log_api_event(
        event_type="predict_error",
        req={"id_employee": 2},
        resp=None,
        http_code=500,
        demo_user_id="test_user",
        duration_ms=150,
        error="test error"
    )

def test_get_raw_employee_trouve():
    """Teste la récupération des infos d’un employé existant via get_raw_employee."""
    emp = get_raw_employee(1)
    assert hasattr(emp, 'to_dict')
    d = emp.to_dict()
    assert "age" in d
    assert d["id_employee"] == 1

def test_get_raw_employee_absent():
    """Teste le cas d’un employé inexistant : doit lever HTTPException 404."""
    with pytest.raises(HTTPException) as exc:
        get_raw_employee(-999)
    assert exc.value.status_code == 404

def test_predict_core():
    """Teste la prédiction sur un employé existant (format, champs, cohérence)."""
    résultat = predict_core(1)
    assert "prediction" in résultat
    assert résultat["prediction"] in ("OUI", "NON")
    assert "score" in résultat
    assert isinstance(résultat["score"], float)
    assert 0.0 <= résultat["score"] <= 1.0
    assert "donnees_brutes" in résultat
    assert "shap_waterfall" in résultat
    assert "shap_waterfall_img" in résultat
    assert "id_employee" in résultat
    assert résultat["id_employee"] == 1

