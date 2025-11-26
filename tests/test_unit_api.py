import os
import numpy as np
import sys
import importlib
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.api import (
    log_model_input,
    log_model_output,
    log_api_event,
    get_raw_employee,
    predict_core,
    get_engine,
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
        error=None,
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
        error="test error",
    )


def test_get_raw_employee_trouve():
    """Teste la récupération des infos d’un employé existant via get_raw_employee."""
    emp = get_raw_employee(1)
    assert hasattr(emp, "to_dict")
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


def test_get_engine_role_inconnu():
    with pytest.raises(ValueError):
        get_engine("unknownrole")


def test_fallback_model_env(monkeypatch):
    monkeypatch.setenv("MODEL_MOCK", "1")
    # Forcer la réimportation pour relancer l'init avec la bonne env
    if "app.api" in sys.modules:
        del sys.modules["app.api"]
    import app.api  # noqa: F401


# Pour la branche logging non-sqlite, un exemple possible selon ton implémentation :
def test_log_model_input_other_dialect(monkeypatch):
    from app import api

    class FakeEngine:
        dialect = type("D", (), {"name": "postgresql"})()

        def connect(self):
            return self

        def begin(self):
            return self

        def execute(self, stmt, *args, **kwargs):
            return None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return None

    monkeypatch.setattr(api, "engine", FakeEngine())
    # Normalement log_model_input doit passer la branche SQL non sqlite
    api.log_model_input({"id_employee": 1})


def test_predict_core_real_pipeline(monkeypatch):
    import numpy as np

    # -- Mock de get_raw_employee --
    class DummyRow:
        def to_dict(self):
            return {"id_employee": 1, "attrition_num": 0, "age": 45, "salaire": 2200}

    monkeypatch.setattr("app.api.get_raw_employee", lambda _id: DummyRow())

    # -- Mock pipeline, preprocessor, estimator --
    dummy_preproc = MagicMock()
    dummy_preproc.transform.return_value = np.array([[0.42, 3.14]])
    dummy_preproc.get_feature_names_out.return_value = ["age", "salaire"]

    dummy_estimator = MagicMock()

    dummy_shap_explanation = MagicMock()
    dummy_shap_explanation.values.tolist.return_value = [0.5, -0.2]
    dummy_shap_values = [dummy_shap_explanation]
    dummy_explainer = MagicMock(return_value=dummy_shap_values)
    dummy_plt = MagicMock()
    dummy_buf = MagicMock()
    dummy_buf.read.return_value = b"testimg"
    dummy_base64 = MagicMock()
    dummy_base64.b64encode.return_value.decode.return_value = "imgb64"

    with patch("app.api.model_pipeline") as mp:
        mp.named_steps = {"preprocessor": dummy_preproc, "estimator": dummy_estimator}
        mp.predict_proba.return_value = [[0.4, 0.6]]
        mp.__class__.__name__ = "NotDummyModel"
        with patch("shap.TreeExplainer", return_value=dummy_explainer):
            with patch("shap.plots.waterfall", return_value=None):
                with patch("matplotlib.pyplot", dummy_plt):
                    with patch("io.BytesIO", lambda: dummy_buf):
                        with patch("base64.b64encode", dummy_base64.b64encode):
                            import app.api

                            res = app.api.predict_core(1)
                            assert res["prediction"] == "OUI"
                            assert res["score"] == 0.6
                            assert "shap_waterfall_img" in res
                            assert res["shap_waterfall"] == {
                                "age": 0.5,
                                "salaire": -0.2,
                            }

    # Variante pour le else (pas de get_feature_names_out)
    del dummy_preproc.get_feature_names_out
    with patch("app.api.model_pipeline") as mp:
        mp.named_steps = {"preprocessor": dummy_preproc, "estimator": dummy_estimator}
        mp.predict_proba.return_value = [[0.4, 0.6]]
        mp.__class__.__name__ = "NotDummyModel"
        with patch("shap.TreeExplainer", return_value=dummy_explainer):
            with patch("shap.plots.waterfall", return_value=None):
                with patch("matplotlib.pyplot", dummy_plt):
                    with patch("io.BytesIO", lambda: dummy_buf):
                        with patch("base64.b64encode", dummy_base64.b64encode):
                            import app.api

                            res2 = app.api.predict_core(1)
                            assert list(res2["shap_waterfall"].keys()) == [
                                "feat_0",
                                "feat_1",
                            ]
