---
title: Attrition Esn Demo
emoji: 🌖
colorFrom: pink
colorTo: red
sdk: docker
pinned: false
license: apache-2.0
short_description: predict attrition in an esn with an existing dataset
---

# Attrition ESN – API & Démo Hugging Face

Démo d’application pour la prédiction du risque d’attrition des salariés d’ESN, basée sur un modèle XGBoost optimisé et déployé derrière une API FastAPI, avec une interface Gradio pour les utilisateurs métier.  
Cette instance utilise une base de données SQL (SQLite sur l’espace HF, PostgreSQL en local/dev) pour stocker les données et les logs.
Sur l'espace Hugging Face, l'API n'est pas exposée publiquement, le fontend gradio l'interroge localement pour illustrer un exemple possible d'utilisation.

---

## Architecture de l’application

- Backend : API FastAPI (`app/api.py`) exposant les endpoints de prédiction, de santé, de liste d’employés et d’inspection des logs.  
- Modèle ML : pipeline scikit-learn + XGBoost, exporté en `model_pipeline.joblib` depuis le projet d’analyse (attrition ESN) et chargé par l’API.  
- Base de données :
  - Dev/local : PostgreSQL (`raw`, `model_input`, `model_output`, `api_log`).
  - HF Space : base SQLite clonée depuis PostgreSQL avec le même schéma.
- Frontend exemple : application Gradio (`gradio_frontend.py`) consommant l’API pour offrir une interface métier (sélection d’ID salarié, prédiction, explicabilité SHAP, consultation des logs).

---

## Principaux endpoints FastAPI

Base URL type :  
`https://<url-API>/`
exemple local : 

- GET `/health`  
  Vérifie l’état du service.  
  Réponse type :
{
"status": "ok",
"version": "1.0",
"env": "hf"
}

- GET `/employee_list`  
Retourne la liste des `id_employee` disponibles dans la table `raw`.

- GET `/predict`  
Paramètre : `id_employee` (int, query param).  
Réponse JSON :
- `prediction` : "OUI" ou "NON".  
- `score` : probabilité prédite de départ (float entre 0 et 1).  
- `id_employee` : identifiant salarié.  
- `donnees_brutes` : features d’origine pour cet employé.  
- `shap_waterfall` : contributions SHAP par feature post-préprocessing.  
- `shap_waterfall_img` : graphique SHAP waterfall encodé en base64 (PNG).

- POST `/predict`  
Payload JSON :
{
"id_employee": 1234
}

Réponse identique à la version GET.

- GET `/log_sample`  
Paramètres :
- `table` : "model_input" | "model_output" | "api_log".  
- `n` : nombre de lignes à retourner (par défaut : 3).  
Utilisé pour afficher un extrait des logs dans l’interface de démo.

---

## Exemple d’utilisation via cURL

### 1. Vérifier l’état de l’API

~~~ bash
curl -X GET "http://127.0.0.1:8000/health"
~~~

### 2. Récupérer la liste des employés

~~~ bash
curl -X GET "http://127.0.0.1:8000/employee_list"
~~~

### 3. Obtenir une prédiction pour un salarié

~~~ bash
curl -X GET
"http://127.0.0.1:8000/predict?id_employee=1495"
~~~

Réponse JSON (exemple simplifié) :

~~~ json
{
"prediction": "OUI",
"score": 0.63,
"id_employee": 1495,
"donnees_brutes": { "...": "..." },
"shap_waterfall": { "age": 0.12, "revenu_mensuel": -0.08 },
[...]
"shap_waterfall_img": "<chaine_base64_png>"
}
~~~

---

## Exemple d’utilisation via le frontend Gradio

L’interface Gradio (`gradio_frontend.py`) est intégrée au Space et communique avec l’API FastAPI.

### Flux principal côté utilisateur

1. Vérifier l’état de l’API  
   - Un bouton "Vérifier l’état de l’API" appelle `GET /health`.  
   - Si `status == "ok"`, la bannière affiche que l’API est opérationnelle et les champs deviennent interactifs.

2. Filtrer et sélectionner un salarié  
   - Un champ texte permet de filtrer la liste d’IDs (`/employee_list`) en tapant quelques chiffres.  
   - La table "Liste filtrée (30 max)" affiche les `id_employee` correspondants.  
   - L’utilisateur copie/colle l’ID choisi dans "ID à prédire".

3. Lancer la prédiction  
   - Le bouton "Prédire" déclenche `GET /predict?id_employee=<ID>`.  
   - La page affiche :
     - Un résumé coloré du risque :
       - 🔴 OUI (risque de départ probable) ou
       - 🟢 NON (risque de départ peu probable).
     - Le score du modèle (probabilité entre 0 et 1).
     - Le graphique SHAP waterfall (image décodée de `shap_waterfall_img`).
     - Un tableau d’explicabilité listant les variables brutes et un indicateur d’impact.

4. Consulter les logs (onglet "Logs API")  
   - Onglet dédié avec les dernières lignes des tables :
     - `model_input` : payloads d’entrée.  
     - `model_output` : prédictions + version de modèle.  
     - `api_log` : événements API (code, durée, erreurs).  
   - Le bouton "Rafraîchir logs" appelle `/log_sample` sur chaque table.

---

## Lancement local

### 1. Préparer la base de données

- Construire PostgreSQL depuis le projet d’analyse (scripts `create_db.py`, `evaluate_db.py`, `log_check.py`).

### 2. Lancer l’API FastAPI

~~~ bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
~~~

Documentation interactive :

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

### 3. Lancer le frontend Gradio

~~~ bash
python gradio_frontend.py
~~~

- Interface : `http://localhost:7860`, connectée à l’API en `http://localhost:8000`.

---

## Stack technique

- Langage : Python 3.10+  
- Backend : FastAPI, Uvicorn  
- Modèle : scikit-learn, XGBoost, SHAP  
- Base de données : PostgreSQL (dev), SQLite (HF), SQLAlchemy pour l’abstraction  
- Frontend : Gradio  
- Tests & CI/CD :
  - Pytest + coverage
  - CI GitHub Actions (lint, tests, coverage, publication rapport)
  - Workflows de release vers HF

---

## À propos

- Projet réalisé dans le cadre de la formation OpenClassrooms AI Engineer.  
- L’espace HF de test est alimenté depuis GitHub via un workflow `release-to-test` après succès de la CI.
- L’espace HF de prod est alimenté depuis GitHub via un workflow `release-to-prod` après succès de `release-to-test`.
