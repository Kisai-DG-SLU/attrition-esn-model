![CI](https://github.com/Kisai-DG-SLU/attrition-esn/actions/workflows/ci.yml/badge.svg)

```markdown
```

***

# Projet – Identification des causes d’attrition au sein d’une ESN

## Table des matières
- [Contexte](#contexte)
- [Objectifs](#objectifs)
- [Préparation de l’environnement Python avec uv](#préparation-de-lenvironnement-python-avec-uv)
- [Arborescence du projet](#arborescence-du-projet)
- [Utilisation & démarrage rapide](#utilisation--démarrage-rapide)
- [Déploiement de l’API](#déploiement-de-lapi)
- [Tests & couverture](#tests--couverture)
- [Déploiement & CI/CD](#déploiement--cicd)
- [Organisation technique](#organisation-technique)
- [Contact & contributions](#contact--contributions)

***

## Contexte

Ce projet a pour objectif d’analyser les phénomènes d’attrition (départs volontaires) au sein d’une Entreprise de Services du Numérique (ESN).  
L’analyse vise à détecter les facteurs principaux influençant la tendance au départ, à partir des données RH, de performance et de sondage interne, afin d’accompagner la prise de décision managériale.

***

## Objectifs

- Mettre en œuvre un workflow complet de data science appliqué au contexte RH.
- Déployer le modèle ML via une API REST.
- Documenter et structurer l’environnement technique selon les standards actuels.
- Interpréter les choix techniques pour garantir reproductibilité et efficacité.
- Professionnaliser la gestion de projet (environnement virtuel, versionning, documentation, modularité).

***

## Préparation de l’environnement Python avec uv

1. **Installation de uv**
   
   ```
   brew install uv
   ```

2. **Initialisation du dossier de projet**
   
   ```
   mkdir attrition-esn
   cd attrition-esn
   uv init
   ```

3. **Ajout des dépendances principales**
   
   ```
   uv add pandas numpy scikit-learn matplotlib seaborn jupyter notebook
   uv add --dev pytest jupyterlab ipython imbalanced-learn shap
   uv add --group lint ruff black
   ```
   Le fichier `pyproject.toml` structure les dépendances (groupes : dev, lint).

4. **Gestion de l’environnement virtuel**
   - uv crée et active `.venv` automatiquement.
   - Synchronisation et portabilité facilitées (`uv sync`).

5. **Gestion du versionning git**
   
   ```
   git init
   echo ".venv/" > .gitignore
   git add .
   git commit -m "Initialisation projet attrition ESN avec uv"
   ```

***

## Arborescence du projet

La structure adoptée vise à séparer exploration, code applicatif, scripts, modèles et tests.

```
.
├── app/                   # Code de l'API (FastAPI, endpoints)
├── data/                  # Données brutes et traitées (non suivies par git)
│   ├── raw/
│   └── processed/
├── models/                # Fichiers de modèles ML sauvegardés
├── notebooks/             # Notebooks d'exploration et de modélisation
├── outputs/               # Résultats générés (figures, prédictions)
├── presentation/          # Supports de présentation (.pptx, .pdf)
├── scripts/               # Scripts utilitaires (prétraitement, fonctions)
├── tests/                 # Tests unitaires/fonctionnels (Pytest)
├── README.md              # Documentation principale
├── pyproject.toml         # Gestion des dépendances (uv)
├── uv.lock                # Verrouillage des dépendances
└── .gitignore             # Exclusions (data, modèles, env, etc.)
```

> *Remarque : certains dossiers sont ajoutés au fur et à mesure de l’avancement.*

***

## Utilisation & démarrage rapide

1. **Cloner le dépôt**
   
   ```
   git clone <url_du_dépôt>
   cd attrition-esn
   ```

2. **Installer les dépendances**
   
   ```
   uv sync
   ```

3. **Lancer l’API (FastAPI)**
   
   ```
   a ecrire
   ```

***

## Déploiement de l’API

L’API expose les prédictions de probabilités d’attrition via des endpoints REST (FastAPI).

### Endpoints disponibles

- `POST /predict` : prédiction sur données RH
- `GET /health` : vérification de l’état de l’API

### Exemple de requête

```
curl -X POST ... ( a ecrire ) 
```

***

## Tests & couverture

Les tests unitaires sont dans le dossier `tests/` :

```
pytest tests/
```

***

## Déploiement & CI/CD

- Pipelines automatisées (GitHub Actions) : installation, lint, tests, build
- Déploiement possible sur serveur cloud, conteneur Docker ou services PaaS

***

## Organisation technique

- **Outils principaux** : Python 3.11+, FastAPI, Scikit-learn, uv, pytest
- **Formats de sauvegarde** : modèles via joblib/json
- **Documentation auto** : endpoints documentés via Swagger (FastAPI)
- **Gestion des secrets et variables sensibles**
Les clés d’API, mots de passe et tout secret technique sont stockés dans un fichier `.env` à la racine du projet.  
Ce fichier n’est jamais versionné (présent dans `.gitignore`) pour garantir la sécurité.  
Un exemple de variables à insérer :

```
API_KEY=xxxxxxx
DB_PASSWORD=xxxxxxxxx
```

**Remarque :** Créez ce fichier manuellement après le clonage.  
Ne partagez jamais vos secrets en public ni dans le repo.

***

## Standards de code et d’expérimentation Machine Learning

- Le code est organisé par modules :
    - `app/` pour l’API (FastAPI)
    - `notebooks/` pour l’exploration et l’expérimentation
    - `models/` pour les modèles sauvegardés
    - `tests/` pour les tests automatisés
- Les dépendances sont gérées via `uv`/`pyproject.toml` et listées dans `requirements.txt`.
- Respect strict de la PEP8 : lint automatique via [ruff](https://docs.astral.sh/ruff/) et formatage avec [black](https://black.readthedocs.io/).
- Les fonctions publiques contiennent une docstring (style Google).
- Les notebooks sont nettoyés avant commit (aucune cellule d’erreur, résutats reproductibles, signatures de pipeline/paramètres claires).
- Les expériences ML sont tracées :
    - les seeds et splits sont toujours fixés,
    - les hyperparamètres et scores sont sauvegardés dans les notebooks/scripts,
    - les modèles exportés sont versionnés explicitement (`model-xgb-weighted-v1.pkl`…)
- Les tests (dossier `tests/`) sont automatisés avec [pytest](https://docs.pytest.org/), et exécutés à chaque push par la CI/CD (GitHub Actions).
- Un “sanity check” valide l’intégration CI avant ajout de vrais tests métiers.
- Les branches sont protégées : tout ajout passe par PR et la CI doit être verte pour merger.
- Les conventions de commit sont claires : début par le type (`feat:`, `fix:`, `test:`), description en anglais.

***
## Contact & contributions

Pour toute demande, suggestion ou collaboration :
- [Auteur] Damien GUESDON / Kisai DG SLU

***

