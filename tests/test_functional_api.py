# pytest est import depuis conftest.py


def test_health(client):
    """Teste le endpoint /health (retour OK, version, env connus)."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "env" in data


def test_employee_list(client):
    """Teste le endpoint /employee_list pour la récupération de la liste des employés."""
    resp = client.get("/employee_list")
    assert resp.status_code == 200
    ids = resp.json()
    assert isinstance(ids, list)
    # On sait que nos fixtures injectent les IDs 1 et 2
    assert 1 in ids
    assert 2 in ids


def test_predict_get_valid(client):
    """Teste /predict?id_employee=1 pour un employé existant (résultat OK, format attendu)."""
    resp = client.get("/predict", params={"id_employee": 1})
    assert resp.status_code == 200
    res = resp.json()
    assert "prediction" in res
    assert res["id_employee"] == 1
    assert res["prediction"] in ("OUI", "NON")
    assert isinstance(res["score"], float)


def test_predict_get_inexistant(client):
    """Teste /predict?id_employee=X pour un employé n'existant pas (réponse 404 attendue)."""
    resp = client.get("/predict", params={"id_employee": -987})
    assert (
        resp.status_code == 404 or resp.json().get("detail") == "ID salarié non trouvé"
    )


def test_predict_post_valid(client):
    """Teste /predict [POST] avec un payload correct (résultat OK, format attendu)."""
    resp = client.post("/predict", json={"id_employee": 2})
    assert resp.status_code == 200
    res = resp.json()
    assert "prediction" in res
    assert res["id_employee"] == 2
    assert res["prediction"] in ("OUI", "NON")
    assert isinstance(res["score"], float)


def test_predict_post_inexistant(client):
    """Teste /predict [POST] avec un faux id (réponse 404 attendue)."""
    resp = client.post("/predict", json={"id_employee": -999})
    assert (
        resp.status_code == 404 or resp.json().get("detail") == "ID salarié non trouvé"
    )


def test_log_sample_model_input(client):
    """Teste /log_sample sur la table model_input (valeurs insérées par fixture)."""
    resp = client.get("/log_sample", params={"table": "model_input", "n": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    # Les input_id insérés dans la fixture sont présents
    ids = [row["input_id"] for row in body if "input_id" in row]
    assert 101 in ids or 102 in ids


def test_log_sample_model_output(client):
    """Teste /log_sample sur la table model_output (valeurs insérées par fixture)."""
    resp = client.get("/log_sample", params={"table": "model_output", "n": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    ids = [row["output_id"] for row in body if "output_id" in row]
    assert 201 in ids or 202 in ids


def test_log_sample_api_log(client):
    """Teste /log_sample sur la table api_log (valeurs insérées par fixture)."""
    resp = client.get("/log_sample", params={"table": "api_log", "n": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    log_ids = [row["log_id"] for row in body if "log_id" in row]
    assert 301 in log_ids or 302 in log_ids


def test_log_sample_table_inconnue(client):
    """Teste /log_sample sur une fausse table -> doit retourner une erreur."""
    resp = client.get("/log_sample", params={"table": "tablebidon"})
    assert resp.status_code == 200
    assert resp.json().get("error") == "Table inconnue"
