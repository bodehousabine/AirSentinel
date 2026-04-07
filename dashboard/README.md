# 📊 Dashboard Analytique AirSentinel

> **Interface interactive d'exploration historique, d'aide à la décision sanitaire et de data visualisation avancée**

[![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red?logo=streamlit)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.22-blueViolet?logo=plotly)](https://plotly.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.2-blue?logo=pandas)](https://pandas.pydata.org)

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Structure Modulaire](#-structure-modulaire)
- [Fonctionnement du Cache et des Thèmes](#-fonctionnement-du-cache-et-des-thèmes)
- [Lancement](#-lancement)

---

## 🎯 À propos

Ce tableau de bord constitue l'application principale d'exploration de données, pensée pour les analystes et preneurs de décision publics de l'IndabaX. Contrairement au backend ou à l'API mobile, ce dashboard intègre toutes les composantes IA visuellement (Cartes choroplèthes, courbes ROC temporelles, graphes d'explicabilité de modèle via SHAP).

---

## ✨ Structure Modulaire

Pour des raisons de lisibilité du code Python et pour permettre un système d'onglets réactif, le dashboard a été divisé en blocs "Intelligence d'Affaires".

```
dashboard/                  # Interface Streamlit
│
├── app.py                  # Point d'entrée principal (Layout, Router)
├── utils.py                # Gestion du Loader Sentinel, configuration des pages
├── themes.py               # Générateur de CSS dynamique (Thème Clair 🌞 / Thème Sombre 🌙)
├── i18n.py                 # Traductions (FR / EN)
├── assets.py               # Stockage de liens CDN pour images
└── blocs/                  # Composants Analystiques :
    ├── bloc1_carte.py      # Cartographie dynamique Plotly par Région
    ├── bloc2_kpis.py       # Synthèse des indicateurs (National, Différentiels)
    ├── bloc3_predictions.py# Intégration du modèle temporel ARIMA sur +72h 
    ├── bloc4_alertes.py    # Détection de pics de pollution PMS
    ├── bloc5_decision.py   # Recommandations & Génération de Rapport PDF
    └── bloc6_shap.py       # Explicabilité IA (Local vs Global)
```

---

## 🎨 Fonctionnement du Cache et des Thèmes

### Système de Cache (`@st.cache_data`)
Le jeu de données traitant plus de 50 000 observations, chaque modification de widget entrainerait une relance totale non optimisée. Le tableau de bord décore le chargement CSV/Parquet d'un cache binaire, garantissant une interaction sub-seconde pour l'utilisateur.

### Design System Adaptatif
AirSentinel supporte automatiquement le schéma de votre système par une injection massive de CSS ciblé. Le backend design `themes.py` redéfinit plus de 20 variables chromatiques sans rechargement lourd.

---

## 💻 Lancement

Assurez-vous d'être à la racine globale du projet AirSentinel, puis exécutez la commande suivante :
```bash
streamlit run dashboard/app.py
```
Le dashboard s'ouvrira (par défaut) sur `http://localhost:8501`.
