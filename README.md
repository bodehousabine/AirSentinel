# AirSentinel Cameroun

> **Système d'aide à la décision sanitaire basé sur l'IA — Surveillance et prédiction de la qualité de l'air pour 40 villes camerounaises**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red?logo=streamlit)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![IndabaX](https://img.shields.io/badge/IndabaX-Cameroon%202026-purple)](https://indabax.org)

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Modèle IA](#-modèle-ia)
- [API publique](#-api-publique)
- [Équipe](#-équipe)
- [Références scientifiques](#-références-scientifiques)

---

## 🎯 À propos

AirSentinel Cameroun est un système complet de surveillance et de prédiction de la qualité de l'air, développé dans le cadre du **Hackathon IndabaX Cameroon 2026** par l'équipe **DPA Green Tech**.

### Contexte

- **94%** des villes camerounaises dépassent le seuil OMS PM2.5 (15 µg/m³)
- **0** système de surveillance en temps réel opérationnel avant AirSentinel
- **27 millions** de Camerounais exposés sans information ni alerte précoce

### Solution

Un dashboard interactif couplé à une API publique permettant de :
- Surveiller la qualité de l'air en temps réel pour 40 villes
- Prédire le PM2.5 sur 72 heures avec un modèle hybride RL+ARIMA
- Générer des recommandations sanitaires adaptées à chaque profil
- Calculer un Indice de Risque Sanitaire (IRS) par Analyse en Composantes Principales

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🗺️ **Carte interactive** | 40 villes · prédictions aujourd'hui · filtrage par région |
| 📊 **KPIs nationaux** | PM2.5, IRS, polluant dominant, tendance annuelle |
| 🔮 **Prédictions 72h** | Modèle hybride RL+ARIMA · MAE = 3.456 µg/m³ |
| 🎛️ **Simulateur météo** | Ajustement des paramètres · prédiction temps réel |
| 🏥 **Décision sanitaire** | Recommandations par profil (citoyen/médecin/maire/chercheur) |
| 🌿 **Profil climatique** | Analyse par zone INS Cameroun (2019) |
| 📄 **Export PDF/CSV** | Rapport sanitaire complet · données brutes |
| 🌐 **API publique** | 7 endpoints REST · documentation Swagger |
| ⚡ **Mise à jour auto** | GitHub Actions · 03h00 UTC · données Open-Meteo |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SOURCES DE DONNÉES                       │
│  Open-Meteo API (météo + pollution) · Gratuit · Temps réel  │
└─────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  PIPELINE DE DONNÉES                         │
│  update_daily.py → Feature Engineering → Parquet            │
│  40 villes · 10 régions · 3 zones INS · 53 520 obs.        │
└─────────────────────┬───────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌─────────────────┐       ┌─────────────────────┐
│  MODÈLE HYBRIDE │       │   INDICE IRS (ACP)  │
│  Régression     │       │  5 variables        │
│  Linéaire +     │       │  2 composantes      │
│  ARIMA          │       │  Normalisé 0-1      │
│  R²=0.893       │       │  INS Cameroun(2019) │
│  MAE=3.456 µg/m³│       └─────────────────────┘
└────────┬────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE UTILISATEUR                     │
│                                                             │
│  Dashboard Streamlit          API FastAPI                   │
│  ├── Bloc 1 : Carte           ├── GET /villes               │
│  ├── Bloc 2 : KPIs            ├── GET /predict/{ville}      │
│  ├── Bloc 3 : Prédictions     ├── GET /alerte/{ville}       │
│  ├── Bloc 4 : Alertes         ├── GET /national             │
│  ├── Bloc 5 : Décision        └── GET /historique/{ville}   │
│  └── Bloc 6 : Profil clima.                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prérequis

- Python 3.11+
- Git

### Cloner le dépôt

```bash
git clone https://github.com/bodehousabine/AirSentinel.git
cd AirSentinel
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 💻 Utilisation

### Lancer le dashboard

```bash
cd dashboard
streamlit run app.py
```

Le dashboard sera disponible sur `http://localhost:8501`

### Lancer l'API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Documentation interactive : `http://localhost:8000/docs`

### Mise à jour manuelle des données

```bash
python update_daily.py
```

---

## 📁 Structure du projet

```
AirSentinel/
│
├── pwa/                        # Application Mobile Web (PWA)
│   ├── index.html              # Vue mobile · Appels API asynchrones
│   ├── sw.js                   # Service Worker · Mode Hors-ligne
│   └── manifest.json           # Manifest pour installation Native
│
├── dashboard/                  # Interface Streamlit
│   ├── app.py                  # Point d'entrée principal
│   ├── utils.py                # Fonctions utilitaires + IRS
│   ├── assets.py               # Images et ressources
│   ├── i18n.py                 # Traductions FR/EN
│   └── blocs/
│       ├── bloc1_carte.py      # Carte interactive
│       ├── bloc2_kpis.py       # KPIs nationaux
│       ├── bloc3_predictions.py# Prédictions 72h + simulateur
│       ├── bloc4_alertes.py    # Système d'alertes
│       ├── bloc5_decision.py   # Décision sanitaire + PDF
│       └── bloc6_shap.py       # Profil climatique par zone
│
├── api/
│   └── main.py                 # API FastAPI 7 endpoints
│
├── deployment/                 # Configurations Déploiement
│   └── render.yaml             # CI/CD Render architecture
│
├── models/                     # Modèles entraînés
│   ├── meilleur_modele.pkl     # Régression linéaire
│   ├── scaler.pkl              # StandardScaler
│   ├── features.pkl            # Features sélectionnées
│   ├── arima_par_zone.pkl      # ARIMA par zone climatique
│   ├── pca_irs.pkl             # ACP pour l'IRS
│   ├── scaler_acp_irs.pkl      # Scaler ACP
│   ├── cols_irs.pkl            # Colonnes IRS
│   ├── seuils_irs.pkl          # Seuils normalisation IRS
│   └── seuils_contextuels.pkl  # Seuils p90 par ville
│
├── data/
│   └── processed/
│       └── dataset_final.parquet
│
├── notebooks/
│   ├── 01_chargement_nettoyage.ipynb
│   ├── 02_tests_statistique.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modelisation.ipynb
│   ├── 05_irs_episodes.ipynb
│   ├── 06_shap_interpretation.ipynb
│   └── 07_analyse_residus.ipynb
│
├── rapport/                    # Documentation
│   └── Rapport_Scientifique.pdf
│
├── .github/
│   └── workflows/
│       └── update_daily.yml    # GitHub Actions · 03h00 UTC
│
├── update_daily.py
├── backfill_missing.py
├── requirements.txt
└── README.md
```

---

## 🤖 Modèle IA

### Modèle Hybride Régression Linéaire + ARIMA

**Zones climatiques INS Cameroun (2019) :**

| Zone | Régions | Caractéristiques |
|---|---|---|
| Zone équatoriale | Centre, Est, Sud, Littoral, Sud-Ouest, Ouest, Nord-Ouest | Forêt équatoriale · 2 saisons des pluies |
| Zone soudanienne | Adamaoua, Nord | Savane · 5-6 mois saison sèche |
| Zone soudano-sahélienne | Extrême-Nord | Steppe · Harmattan · Dust dominant |

**Performances sur données test 2025 :**

| Métrique | Modèle | Baseline | Amélioration |
|---|---|---|---|
| R² | **0.893** | — | — |
| MAE | **3.456 µg/m³** | 11.647 µg/m³ | **-70.3%** |
| RMSE | **5.088 µg/m³** | — | — |
| Pics > 35 µg/m³ | **79.6%** corrects | — | — |

### Indice de Risque Sanitaire (IRS)

Calculé par ACP sur 5 variables : PM2.5, Dust, CO, UV, Ozone  
2 composantes · Variance expliquée : 55.1% + 28.0% · Normalisé 0-1

**Niveaux basés sur percentiles historiques p50/p75/p90 :**

```
IRS < p50  →  FAIBLE    (vert)
IRS < p75  →  MODÉRÉ    (ambre)
IRS < p90  →  ÉLEVÉ     (orange)
IRS ≥ p90  →  CRITIQUE  (rouge)
```

### Cas d'usage validé

> Le 13 février 2025, un pic critique de **110.3 µg/m³** a été enregistré à Bertoua (7.4x le seuil OMS).  
> Notre modèle l'a prédit à **101.8 µg/m³** avec une erreur de seulement **8.4 µg/m³**.

---

## 🌐 API publique

```bash
# Prédictions pour une ville
GET /predict/Yaounde

# Niveau d'alerte + recommandations
GET /alerte/Maroua

# Résumé national
GET /national
```

**Exemple de réponse :**
```json
{
  "ville": "Yaounde",
  "zone": "Zone équatoriale",
  "predictions": [
    {"label": "Aujourd'hui",  "pm25_predit": 11.76, "niveau": "FAIBLE"},
    {"label": "Demain",       "pm25_predit": 13.10, "niveau": "FAIBLE"},
    {"label": "Après-demain", "pm25_predit": 11.38, "niveau": "FAIBLE"}
  ],
  "modele": {"r2": 0.893, "mae": 3.456}
}
```

---

## 👥 Équipe

**DPA Green Tech — IndabaX Cameroon 2026**

| Membre | Institution | Rôle |
|---|---|---|
| **BODEHOU Sabine** | ISSEA Yaoundé | Collecte données · Feature Engineering · Blocs 1 & 2 |
| **FANKAM Marc Aurel** | ISSEA Yaoundé | Modélisation · IRS · Blocs 3, 5 & 6 |
| **PEURBAR RIMBAR Firmin** | ISSEA Yaoundé | EDA · SHAP · Bloc 4 |
| **FOFACK ALEMDJOU Henri Joël** | ENSP Yaoundé | Frontend & API |

---

## 📚 Références scientifiques

| Référence | Usage |
|---|---|
| **WHO AQG 2021** · NCBI NBK574591 | Seuils PM2.5 (15/25/37.5/50/75 µg/m³) |
| **INS Cameroun (2019)** | Zones climatiques · données démographiques |
| **Chen & Hoek (2020)** | Impact sanitaire PM2.5 · mortalité |
| **Schepanski et al. (2007)** | Transport de poussière saharienne |
| **Knippertz et al. (2008)** | Mécanismes harmattan |
| **Gordon et al. (2023)** · PMC9884662 | Feux de brousse · Afrique subsaharienne |
| **Barker et al. (2020)** | CO et épisodes de feux |
| **Box & Jenkins (1976)** | Modélisation ARIMA |
| **IPCC AR5 (2014)** | Changement climatique · Afrique centrale |

---

## 📄 Licence

MIT License

---

*AirSentinel Cameroun · DPA Green Tech · IndabaX Cameroon 2026*  
*Coût d'exploitation : **0 FCFA** · Données Open-Meteo · Mise à jour quotidienne automatique*
