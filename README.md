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
- **Simulateur Interactif (AI Lab)** : Manipulez les variables météo pour voir l'impact immédiat sur le PM2.5.
- **Alertes Temps Réel (SMTP)** : Abonnez-vous à une ville pour recevoir des notifications mail en cas d'alerte.
- **Interprétabilité (SHAP)** : Compréhension détaillée de l'impact de chaque variable sur les prédictions.
- **Dashboard Premium (PWA)** : Interface Next.js 15 ultra-moderne avec glassmorphism et animations fluides.
- **API RESTful** : Backend performant avec FastAPI pour exposer le modèle de prédiction.

---

## 📂 Structure du Projet

L'arborescence des dossiers et fichiers principaux de l'application :

```text
AirSentinel/
├── api/                   # Backend FastAPI
│   ├── routers/           # Endpoints (Prédictions, Alertes, Users...)
│   ├── services/          # Logique métier (Mail, Calculs, Data...)
│   ├── models/            # Modèles de base de données (SQLAlchemy)
│   └── main.py            # Point d'entrée principal
├── pwa/airsentinel        # Frontend Moderne (Next.js 15)
│   ├── src/app/dashboard  # Pages du tableau de bord
│   └── src/services       # Clients API (Axios)
├── dashboard/             # Ancien Dashboard (Streamlit - Backup)
├── data/                  # Données brutes et préparées
├── models/                # Fichiers de modèles ML (.joblib)
├── notebooks/             # Notebooks de Data Science
└── README.md
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

Le projet est divisé en deux services principaux : l'API de prédiction et l'interface PWA moderne.

### Lancer l'API (Backend)
L'API sert le modèle Machine Learning et gère les abonnements aux alertes.
```bash
uvicorn api.main:app --reload
```
Documentation Swagger : `http://127.0.0.1:8000/api/v1/docs`.

### Lancer la PWA (Frontend Moderne)
Navigateur recommandé : Chrome/Edge pour support PWA.
```bash
cd pwa/airsentinel
npm install
npm run dev
```
Accès : `http://localhost:3000/dashboard/predictions`.

### Configuration des Alertes (SMTP)
Créez un fichier `api/.env` à partir de `api/.env.example` et renseignez vos identifiants SMTP (Gmail, SendGrid, etc.) pour activer les notifications par mail.

---

## 💻 Pile Technologique
- **Backend** : FastAPI, SQLAlchemy, Pydantic, Uvicorn
- **Frontend** : Next.js 15 (App Router), Tailwind CSS v4, Framer Motion, Lucide Icons, Recharts
- **Data Science** : Pandas, Scikit-learn, XGBoost, LightGBM, SHAP
- **Base de Données & Stockage** : Supabase (Auth/Storage/Postgres)
- **Notification** : SMTP Protocol
