---
marp: true
theme: gaia
class: lead
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
paginate: true
_paginate: false
style: |
  section {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    font-family: 'Arial', sans-serif;
    font-size: 28px;
    height: 100%;
    padding: 40px;
  }
  h1 { color: #0060df; font-size: 1.5em; margin-top: 0; }
  h2 { color: #333; font-size: 1.2em; }
  h3 { color: #444; font-size: 1.0em; margin-bottom: 10px; }
  
  /* Blocs de code compacts */
  pre {
    font-size: 0.55em;
    background-color: #f4f4f4;
    padding: 10px;
    border-radius: 5px;
    overflow-x: hidden;
  }
  
  /* Colonnes */
  .columns {
    display: grid;
    grid-template-columns: 55% 45%;
    gap: 1rem;
    align-items: start;
  }
  
  /* Images standards */
  img { box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; }

  /* Images spécifiques (arborescence) pour ne pas déborder */
  .tree-img img {
    max-height: 580px;
    width: auto;
    object-fit: contain;
  }
  .workflow-img img {
    max-height: 400px;
    width: auto;
    object-fit: contain;
  }
  .coverage-img img {
    max-height: 300px;
    width: auto;
    object-fit: contain;
  }
  .gradio-img img {
    max-height: 200px;
    width: auto;
    object-fit: contain;
  }

  /* Mermaid compact */
  .mermaid {
    display: flex;
    justify-content: center;
    background-color: transparent;
  }
  .mermaid svg { max-height: 280px; }
  
  /* Footer info */
  .grey-info {
    color: #666;
    font-size: 0.8em;
    margin-top: auto;
    border-top: 1px solid #ddd;
    padding-top: 10px;
  }
---

<!-- _class: invert -->

# Déploiement d'un modèle de Machine Learning
## Soutenance Projet 5 - Attrition ESN

<div class="grey-info">

**Damien Guesdon**
*Rôle : Machine Learning Engineer*
*Destinataire : Resp. Technique (Futurisys)*
*Date : Décembre 2025*

</div>

<!-- note:
Bonjour.
Je vous présente aujourd'hui l'industrialisation du modèle de prédiction d'attrition pour TechNova.
L'objectif de cette mission était de passer d'un notebook d'analyse à une architecture logicielle robuste, testée et déployée.
J'ai structuré la présentation selon les 5 livrables attendus : Git, API, Tests, BDD et Résultats.
-->

---

# 1. Structure du Dépôt Git & Workflow

<div class="columns">
<div>

### Architecture Modulaire
- **`app/`** : API FastAPI & Frontend Gradio.
- **`data/` & `scripts/`** : Gestion des données et BDD.
- **`tests/`** : Tests unitaires et fonctionnels.
- **Racine** : Fichiers de configuration (`environment.yml`, `requirements.txt`) et workflows CI/CD.

### Workflow Git
- Branches : `main`, `feat/<feature>` (dev), </br>`test` (HF **Test**), `prod` (HF **Production**)
- Tags sémantiques pour les releases. ![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/Kisai-DG-SLU/attrition-esn-model?label=Version&color=blue)

</div>
<div class="tree-img">

![Arborescence du projet](images/tree.png)

</div>
</div>

<!-- note:
J'ai structuré le projet pour séparer clairement le code applicatif, la logique de données et les tests qualité.
L'usage de Conda en local me permet de gérer finement les environnements, tandis que le requirements.txt assure la reproductibilité dans la CI/CD.
-->

---

# 2. Pipeline CI/CD (Workflow GitOps)

Stratégie à 3 niveaux pour garantir la qualité et la sécurité.

<div class="workflow-img">

![](images/workflow.png)

</div>

- **Optimisation :** Déploiement sélectif (uniquement `app/`) vers Hugging Face.
- **Sécurité :** Injection des secrets (`HF_TOKEN`) à la volée.

<!-- note:
C'est le cœur de l'industrialisation.
Le pipeline CI bloque tout code non conforme.
Le déploiement se fait en cascade : d'abord sur un environnement de test, puis, après validation, en production.
C'est une approche professionnelle qui minimise les risques de régression.
-->

---

# 3. API FastAPI & Documentation

L'API (`app/api.py`) est le point d'entrée unique du système.

<div class="columns">
<div>

### Fonctionnalités
- **Prédiction :** `POST /predict/` (avec log automatique).
- **Observabilité :** `GET /log_sample/` (contrôle des logs).
- **Santé :** `GET /health` (versionning).

### Documentation
- **Swagger UI / ReDoc :** Intégré et interactif.
- **Pydantic :** Validation stricte des données entrantes.

</div>
<div>

### Extrait `api.py`

<div class="workflow-img">

![](images/api-sample.png)

</div>
</div>
</div>

<!-- note:
L'API expose le modèle de manière sécurisée.
Chaque requête est validée par Pydantic et loguée en base de données avant même d'être traitée.
Cela garantit une traçabilité totale des décisions du modèle.
-->

---

# 4. Tests & Qualité (Pytest)

Couverture élevée (**~86%**) garantissant la robustesse.

<div class="columns">
<div>

### Stratégie de Tests
- **Unitaires (`test_unit_api.py`) :**
  - Isolation via **Mock** (BDD, Modèle).
  - Teste la logique interne.
- **Fonctionnels (`test_functional_api.py`) :**
  - Simulation HTTP complète (`Test Client`).
  - Vérification des codes erreurs (404, 422).

</div>
<div>

### Rapport de Couverture

<div class="coverage-img">

![](images/coverage.png)

</div>

*(Généré par la CI via `coverage run`)*

</div>
</div>

<!-- note:
La qualité logicielle est validée par une suite de tests complète.
Les tests unitaires vérifient la logique métier, tandis que les tests fonctionnels valident le comportement de l'API dans son ensemble.
Un rapport de couverture est généré à chaque commit pour s'assurer qu'on ne baisse pas la garde.
-->

---

# 5. Base de Données : Stratégie Hybride

Adaptation pragmatique aux contraintes d'infrastructure.

<div class="columns">
<div>

### Architecture Duale
1. **Dev (Local) : PostgreSQL**
   - Robustesse, types forts.
   - Script `create_db.py`.
2. **Prod (HF Spaces) : SQLite**
   - Portabilité (Fichier `.sqlite`).
   - Script de migration `pg_to_sqlite_export.py`.

### Schéma Audit (`schema.sql`)
- `model_input` & `model_output`.

</div>
<div>

### Abstraction SQLAlchemy

<div class="coverage-img">

![](images/alchemy.png)

</div>

*Le code de l'application ignore la BDD sous-jacente.*
</div>
</div>

<!-- note:
Pour gérer la persistance sur des environnements conteneurisés éphémères (Hugging Face), j'ai opté pour une stratégie hybride.
Je développe sur PostgreSQL pour la rigueur (la gestion des droits), et je déploie sur SQLite pour la simplicité.
Une couche d'abstraction (SQLAlchemy) rend le code applicatif totalement agnostique du moteur de base de données.
-->

---

# 6. Cas d'Usage & Résultats

Le modèle **XGBoost** au service de la rétention des talents.

<div class="columns">
<div>

### Interface Métier (Gradio)
- **Utilisateur :** RH.
- **Action :** Saisir ID Employé -> Obtenir Risque.
- **Plus-value :** Explicabilité **SHAP**.

### Performance
- **Métrique :** Optimisation du **Recall**.
- **Pourquoi ?** Ne rater aucun départ potentiel (Coût Faux Négatif > Coût Faux Positif).

</div>
<div>

<div class="gradio-img">

![](images/gradio.png)

</div>

### Démonstration
- **Score de risque** (ex: 60%)
- **Facteurs clés :**
  - *Fréquence des déplacements*
  - *Heures supplémentaires*
  - *Satisfaction Environnement*

</div>
</div>

<!-- note:
L'interface finale permet aux RH d'identifier les profils à risque.
L'intégration native des graphiques SHAP permet de comprendre les causes racines du risque (salaire, distance, etc.), transformant la prédiction en plan d'action.
-->

---

# 7. Conclusion & Débrief

### Bilan Technique
- ✅ **Architecture Propre :** Séparation API / Data / Tests.
- ✅ **Pipeline DevOps :** CI/CD complet (Lint, Black, Test, Deploy).
- ✅ **Observabilité :** Système de logs prêt pour le monitoring.

### Défis Relevés
1. **Parité BDD :** Gestion transparente Postgres/SQLite via SQLAlchemy.
2. **Gestion des Secrets :** Sécurisation des accès dans un contexte Open Source.

**Place aux questions.**

<div class="grey-info">
Damien Guesdon - Projet 5 OpenClassrooms
</div>
