```markdown

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
  a écrire 
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

***

## Contact & contributions

Pour toute demande, suggestion ou collaboration :
- [Auteur] daminou / Kisai DG SLU
- Issues & PR bienvenues sur le repo GitHub.

***
