# 🧠 Modèles d'Intelligence Artificielle

> **Le cerveau mathématique d'AirSentinel : Traitement des Séries temporelles par méthode hybride (Régression + ARIMA) & ACP**

[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-f9a03c?logo=scikitlearn)](https://scikit-learn.org)
[![Statsmodels](https://img.shields.io/badge/TimeSeries-Statsmodels-darkblue)](https://www.statsmodels.org/)
[![Joblib](https://img.shields.io/badge/Serialization-Joblib-green)](#)

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Algorithmique Hybride & Climatisation](#-algorithmique-hybride--climatisation)
- [Évaluation Statistique de l'IRS](#-évaluation-statistique-de-lirs)
- [Inventaire des Artefacts](#-inventaire-des-artefacts)

---

## 🎯 À propos

Ce répertoire stocke les artefacts pré-entraînés qui fournissent tout le potentiel prédictif aux 40 villes ciblées par AirSentinel lors de l'IndabaX Cameroon 2026. Plutôt que de ré-entrainer des modèles en ligne lors d'une requête HTTP, les matrices de décision générées au format `.pkl` permettent des calculs foudroyants en production.

---

## 🧬 Algorithmique Hybride & Climatisation

La complexité des particules (PM2.5) tient au fait qu'elles corrèlent aux événements exogènes (Température, Humidité, Feux), mais aussi au cycle des mois et années. 

Notre Solution adopte un modèle **Hybride Random Forest (Linear regression base) + ARIMA** :
- **Tronc de Base** : Analyse les corrélations quantitatives brutes entre les entités.
- **Intervention Régressive Temporelle (ARIMA)** : Un deuxième composant capte ce que le modèle originel n'a pas pu évaluer. Cet ARIMA est segmenté spatialement ! Il y a un sous-modèle pour la **Forêt équatoriale**, un pour la **Savane (soudanienne)**, et un pour l'**Harmattan poussiéreux (soudano-sahélienne)**.


| Métrique | Performance Test Set (2025) | Amélioration relative |
|---|---|---|
| Modèle R² | **0.893** | *Excellent Fit (Très fort)* |
| Erreur Absolue (MAE)| **3.456 µg/m³** | *baisse de -70.3% face baseline* |
| Pics identifiés | **79.6% corrects** | *Prévention épidémiologique forte* |

---

## 📊 Évaluation Statistique de l'IRS (Indice de Risque)

L'IRS (Indice de Risque Sanitaire) n'est pas qu'une lecture d'un gaz unique, c'est l'essence du Dashboard.
Il est calculé par une **Analyse en Composantes Principales (ACP/PCA)** reposant sur : PM2.5, Dust, CO, UV, et Ozone.
* La variance expliquée globale justifie un lissage statistique entre 0 et 1 (min-max). 
* L'indicateur s'aligne ensuite sur les percentiles mathématiques majeurs régionnaires (p50, p75, p90) pour calibrer les seuils Modérés ou Critiques.

---

## 📦 Inventaire des Artefacts (`.pkl`)

Pour assurer une inférence parfaite, le serveur (via FastAPI) charge ces modèles au démarrage (Warm-up) :

```
models/
│
├── meilleur_modele.pkl     # Cœur régresseur
├── scaler.pkl              # Normalisateur Z-Score (Feature engineering à la volée)
├── features.pkl            # Colonnes requises
├── arima_par_zone.pkl      # Tensor ARIMA divisé par zone climatique INS
├── pca_irs.pkl             # Matrice ACP pour la projection
├── scaler_acp_irs.pkl      # Pré-scaler pour la pondération IRS
└── seuils_*.pkl            # Délimitations structurelles p50/p75/p90
```
