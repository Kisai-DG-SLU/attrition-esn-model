# Attrition ESN – API Démo

Démo d’application pour la prédiction du risque d’attrition des salariés d’ESN, basée sur un modèle XGBoost optimisé.  
Cette instance utilise une base de données SQL (SQLite sur l’espace HF, PostgreSQL en local/dev) pour stocker toutes les données exploitées par l’application.

---

## Fonctionnement

- Les données des salariés sont **préchargées** dans la base SQL.
- L'utilisateur interagit avec une **API FastAPI** (mode Docker/HF Space).
- Un endpoint principal (`/predict`) permet d’obtenir le score d’attrition d’un salarié sélectionné, ainsi qu’un graphe explicatif type waterfall (SHAP) pour la compréhension du modèle.

---

## Principaux Endpoints API

- **GET /health**  
  Vérifie l’état du service.
- **POST /predict**  
  Requiert l’ID d’un salarié (`employee_id`) en entrée.  
  Retourne :
    - Score de risque d’attrition
    - Graphique waterfall d’explicabilité au format image/base64
    - Interprétation des variables clés
- **(optionnel)** endpoints de listing ou auto-complétion sur `employee_id`

---

## Utilisation

- **Via l’API** :
    - Exemple de requête :
        ```
        curl -X POST "https://hf.space/embed/damienguesdon/attrition-esn-demo-test/predict" \
             -H "Content-Type: application/json" \
             -d '{"employee_id": 1234}'
        ```
- **Interface utilisateur** :
    - Sélectionnez l’ID salarié dans une liste filtrable/auto-complétée.
    - Cliquez sur “Prédire” pour voir le score et le graphe explicatif.

---

## Workflow & Persistence

- Tous les inputs utilisateurs et outputs du modèle sont enregistrés dans la base de données pour audit & analyse.
- SQLAlchemy est utilisé pour garantir la portabilité entre PostgreSQL (dev/local) et SQLite (HF Space).

---

## Dépendances Principales

- Python 3.10+
- fastapi
- uvicorn
- xgboost
- shap
- sqlalchemy
- pandas
- sqlite3 ou psycopg2 selon le contexte
- (voir requirements.txt minimal dédié Space)

---

## À propos

- Projet réalisé dans le cadre **OpenClassrooms IA Engineer**.
- Environnement de test & prod distincts, synchronisation manuelle (prod) ou automatique (test) depuis GitHub
- Licence recommandée : MIT ou Apache 2.0

---

## Contact

Pour support, questions ou retours :  
[https://github.com/Kisai-DG-SLU/attrition-esn-model]

---
