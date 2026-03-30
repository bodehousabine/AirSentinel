# 🌍 AirSentinel Cameroun
> Système IA de prédiction qualité air — IndabaX 2026

Ce projet est conçu pour apporter des solutions technologiques concrètes et innovantes aux défis de notre environnement en prédisant la qualité de l'air au Cameroun. Il intègre une modélisation avancée, une API robuste et un tableau de bord interactif complet.

## 👥 Équipe DPA Green Tech
- **BODEHOU Sabine** (ISSEA) — Data Science
- **FANKAM Marc Aurel** (ISSEA) — Modélisation
- **PEURBAR RIMBAR Firmin** (ISSEA) — SHAP & Rapport
- **FOFACK ALEMDJOU Henri Joël** (ENSP) — Frontend & API

---

## ✨ Fonctionnalités Clés
- **Prédiction IA** : Estimation de la qualité de l'air basée sur des modèles XGBoost/LightGBM.
- **Interprétabilité (SHAP)** : Compréhension détaillée de l'impact de chaque variable sur les prédictions.
- **Tableau de Bord Interactif** : Interface utilisateur riche construite avec Streamlit.
- **API RESTful** : Backend performant avec FastAPI pour exposer le modèle de prédiction.
- **Support PWA** : Accessible en tant que Progressive Web App.

---

## 📂 Structure du Projet

L'arborescence des dossiers et fichiers principaux de l'application :

```text
AirSentinel/
├── api/                   # Code de l'API RESTful
│   └── main.py            # Point d'entrée principal de FastAPI
├── dashboard/             # Application interface utilisateur
│   ├── app.py             # Script principal de l'application Streamlit
│   ├── blocs/             # Composants modulaires de l'UI
│   ├── utils/             # Fonctions utilitaires
│   ├── assets.py          # Gestion des assets (images, logos)
│   ├── chatbox.py         # Module de chat intégré
│   ├── landing.py         # Page d'accueil du dashboard
│   ├── themes.py          # Configuration des thèmes visuels
│   └── translations.py    # Textes et traductions de l'application
├── data/                  # Données du projet de modélisation
│   ├── raw/               # Données brutes
│   └── processed/         # Données nettoyées et préparées
├── deployment/            # Configurations de déploiement
│   └── render.yaml        # Fichier de config pour le service Render
├── graphiques/            # Résultats visuels générés par les notebooks (SHAP, corrélations)
├── models/                # Fichiers de modèles ML entraînés (joblib)
├── notebooks/             # Notebooks Jupyter pour la science des données
│   ├── 01_chargement_nettoyage.ipynb
│   ├── 02_tests_statistiques.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modelisation.ipynb
│   ├── 05_irs_episodes.ipynb
│   └── 06_shap_interpretation.ipynb
├── pwa/                   # Configuration Progressive Web App
│   └── manifest.json
├── rapport/               # Documents et rapports générés
├── README.md              # Documentation principale (ce fichier)
└── requirements.txt       # Dépendances Python nécessaires au projet
```

---

## 🛠️ Installation et Prérequis

### 1. Cloner le dépôt et aller dans le dossier
```bash
git clone <URL_DU_DEPOT>
cd AirSentinel
```

### 2. Créer un environnement virtuel (Recommandé)
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

---

## 🚀 Utilisation

Le projet est divisé en deux services principaux : l'API de prédiction et le Dashboard utilisateur.

### Lancer l'API (Backend)
L'API sert le modèle Machine Learning (FastAPI).
```bash
uvicorn api.main:app --reload
```
L'API sera disponible à l'adresse locale `http://127.0.0.1:8000`. Vous pouvez consulter la documentation de l'API sur `http://127.0.0.1:8000/docs`.

### Lancer le Dashboard (Frontend)
L'application Streamlit pour l'interaction utilisateur.
```bash
streamlit run dashboard/app.py
```
Le dashboard s'ouvrira automatiquement dans votre navigateur par défaut (généralement `http://localhost:8501`).

---

## 💻 Pile Technologique
- **Langage** : Python 3
- **Data Science** : Pandas, NumPy, Scikit-learn, XGBoost, LightGBM, SHAP, SciPy
- **Visualisation** : Matplotlib, Seaborn, Plotly, Folium
- **Backend/API** : FastAPI, Uvicorn
- **Frontend** : Streamlit
