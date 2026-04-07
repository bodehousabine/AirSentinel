# 📓 Notebooks de Recherche & Expérimentation (Data Science)

> **Laboratoire R&D d'AirSentinel — De la collecte brute à l'interprétabilité des modèles (XAI)**

[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter)](https://jupyter.org)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-f9a03c?logo=scikitlearn)](https://scikit-learn.org)

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Pipeline Expérimental](#-pipeline-expérimental)
- [Détails des Notebooks](#-détails-des-notebooks)
- [Utilisation](#-utilisation)

---

## 🎯 À propos

Ce répertoire contient l'intégralité de la démarche scientifique de l'équipe **DPA Green Tech**. Chaque notebook représente une étape charnière du projet, garantissant la reproductibilité des résultats présentés lors de l'IndabaX Cameroon 2026. Nous passons ici de données brutes à un système prédictif robuste et explicable.

---

## ✨ Pipeline Expérimental

Le workflow suit une progression logique de Data Engineering et de modélisation :

| Étape | Notebook | Description |
|---|---|---|
| 1 | `01_chargement_nettoyage.ipynb` | Connexion aux APIs, agrégation des sources et nettoyage des valeurs aberrantes. |
| 2 | `02_tests_statistiques.ipynb` | Analyse exploratoire (EDA), tests de stationnarité et corrélations de Pearson/Spearman. |
| 3 | `03_feature_engineering.ipynb` | Création de variables (Lags, Moyennes mobiles, Encodage des zones climatiques). |
| 4 | `04_modelisation.ipynb` | Entraînement du modèle hybride (Linear Regression + ARIMA) et optimisation des hyperparamètres. |
| 5 | `05_irs_episodes.ipynb` | Calcul de l'Indice de Risque Sanitaire (IRS) par ACP et détection d'épisodes critiques. |
| 6 | `06_shap_interpretation.ipynb` | Analyse de l'importance des variables via SHAP (Explicabilité globale et locale). |
| 7 | `07_analyse_residus_final.ipynb` | Diagnostic final du modèle, analyse des erreurs et validation de la précision. |

---

## 🏗️ Détails des Notebooks

### 🧪 02 - Tests Statistiques
Ce notebook est crucial car il valide l'hypothèse de saisonnalité du PM2.5 au Cameroun, justifiant l'utilisation d'une composante ARIMA pour chaque zone climatique.

### 🧠 06 - Interprétation SHAP
Nous utilisons **SHAP (SHapley Additive exPlanations)** pour briser l'effet "boîte noire" de l'IA. Ce notebook démontre comment la poussière (Dust) et l'humidité impactent spécifiquement les prédictions dans le Grand Nord par rapport au Littoral.

---

## 💻 Utilisation

Pour explorer ces notebooks localement :
1. Installez les dépendances :
   ```bash
   pip install notebook jupyterlab
   ```
2. Lancez l'interface :
   ```bash
   jupyter lab
   ```
3. Naviguez dans le dossier `notebooks/` et ouvrez le fichier de votre choix.

---

*AirSentinel · Laboratoire Data Science · DPA Green Tech*
