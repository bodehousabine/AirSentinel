# 🗄️ Moteur de Données & ETL AirSentinel

> **L'usine logistique silencieuse qui automatise, nettoie et formate la qualité d'historique (50k+ chroniques Temporelles) du projet**

[![Parquet](https://img.shields.io/badge/Format-Parquet-orange?logo=apacheparquet)](https://parquet.apache.org/)
[![Pandas](https://img.shields.io/badge/Pipeline-Pandas-blue?logo=pandas)](https://pandas.pydata.org)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-Github%20Actions-lightgrey?logo=github)](https://github.com/features/actions)

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Formats de Stockage Avancé](#-formats-de-stockage-avancé)
- [Automatisation Quotidienne (GitHub Actions)](#-automatisation-quotidienne-github-actions)

---

## 🎯 À propos

Le module de la sous-délégation des données est responsable de récolter publiquement, nettoyer et transformer les entrées (Météo, Gaz toxiques, Particules en Suspension). Il génère un output compact que toute l'équipe Machine Learning de DPA Green Tech manipule pour ses modélisations.

---

## ✨ Formats de Stockage Avancé (`.parquet`)

```
data/
└── processed/
    └── dataset_final.parquet
```

Au fil des années d'observation sur le territoire, les entrées horaires font exploser la lenteur de simple fichier `.csv`. La base est stockée en format **`.parquet`**. L'utilisation de cet arbre binaire organisé en colonnes nous garantit :
- Un fichier **10x plus léger** à charger dans la mémoire vive des environnements Render.
- Un scan analytique **extrêmement performant** permettant un rafraichissement parfait du Streamlit lors des filtres massifs de dates.

---

## 🔄 Automatisation Quotidienne (GitHub Actions)

Situé à la racine du projet, vous trouverez les utilitaires cruciaux pilotés par `.github/workflows/update_daily.yml`.

### Script `update_daily.py`
Fonctionnement sous forme d'extraction planifiée :
1. Connexion au registre gratuit **Open-Meteo**.
2. Aspirateur chronologique des 24 heures passées (Humidité, UV, O3, NO2...).
3. Actualisation mathématique et nettoyage quantitatif des variables.
4. Export de la nouvelle table `dataset_final.parquet`.

Le script est exécuté **Chaque Nuit à 03:00 (UTC)** par l'automate GitHub. Sur chaque push réalisé par l'automate, Render re-compile le serveur FastAPI. Résultat : **Une solution de monitoring qui ne requiert strictement aucune maintenance humaine au quotidien.**
