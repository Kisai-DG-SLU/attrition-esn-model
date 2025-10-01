```markdown
# Projet – Identification des causes d’attrition au sein d’une ESN

## Contexte

Ce projet, a pour objectif d’analyser les phénomènes d’attrition (départs volontaires) au sein d’une Entreprise de Services du Numérique (ESN). L’analyse vise à détecter les facteurs principaux influençant la tendance au départ, à partir des données RH, de performance et de sondage interne, pour accompagner la prise de décision managériale.

## Objectifs

- Mettre en œuvre un workflow complet de data science appliqué au contexte RH.
- Structurer et documenter l’environnement technique selon les standards actuels.
- Interpréter les choix techniques et les étapes de réflexion pour garantir reproductibilité et efficacité.
- Professionnaliser la gestion de projet (environnement virtuel, versionning, documentation, modularité).

## Étape préalable : Préparation de l’environnement Python avec uv

### Choix réfléchi de l’outil de gestion d’environnement

Ayant utilisé Poetry sur les projets précédents, une analyse comparative (Poetry vs uv) a été menée :
- **uv** se distingue par sa rapidité, sa gestion native des dépendances et versions Python
- comme poetry, uv intègre maintenant les groupes de dépendances (« dependency-groups »).
- uv simplifie la reproductibilité et facilite la maintenance sur plusieurs projets successifs (9 à venir).
- La migration depuis Poetry étant aisée, uv représente le choix pertinent pour la suite du cursus.

### Déploiement pas à pas (MacBook Pro, git/GitHub)

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

5. **Initialisation du versionning git**
   ```
   git init
   echo ".venv/" > .gitignore
   git add .
   git commit -m "Initialisation projet attrition ESN avec uv"
   ```
   Publication possible sur GitHub pour traçabilité et partage.

6. **Organisation du travail**
   - Dossier `notebooks/` pour l’exploration, la modélisation et la synthèse.
   - Ajout incrémental des dépendances via uv si besoin.

### Réflexion

Ce cheminement illustre le choix professionnel :  
- Prioriser l’efficacité technique (temps de setup, compatibilité, portabilité).
- Documenter chaque étape pour faciliter la transmission, la maintenance et l’audit du projet.
- Justifier les décisions techniques par une analyse comparative fondée et l’expérimentation concrète.
- Maîtriser les outils phares de l’écosystème Python data science, tout en intégrant la notion de workflow reconfigurable pour les futures missions.

---

```
