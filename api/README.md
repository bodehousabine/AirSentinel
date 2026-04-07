# ⚙️ API AirSentinel (FastAPI)

> **Cœur neuronal et point d'interfaçage pour la distribution des prédictions qualité de l'air de 40 villes camerounaises**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Render](https://img.shields.io/badge/Deploy-Render-black?logo=render)](https://render.com)

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Endpoints REST](#-endpoints-rest)
- [Architecture du module](#-architecture-du-module)
- [Déploiement et Lancement](#-déploiement-et-lancement)

---

## 🎯 À propos

Le module `api` constitue le backend de l'écosystème AirSentinel. Il charge le jeu de données local (généré au format Parquet) pour le rendre consommable de façon asynchrone par l'application mobile (PWA) et par tout autre composant requêteur. 
Au lieu de forcer le client mobile à télécharger de gros modèles d'IA, l'API interroge les modèles pré-entraînés stockés dans `/models` pour répondre en temps réel.

---

## ✨ Endpoints REST

| Endpoint | Méthode | Description | Paramètres / Retour |
|---|---|---|---|
| `GET /` | GET | Statut de l'API | Retourne `{"name": "AirSentinel Cameroun API", "status": "active"}` |
| `GET /villes` | GET | Liste des villes disponibles | Renvoie les 40 villes supportées |
| `GET /regions`| GET | Liste des régions | Groupement par région INS |
| `GET /data/{ville}` | GET | Historique brut | 72 heures historiques pour la `ville` |
| `GET /predict/{ville}` | GET | Moteur Prédictif IA | Prédictions PM2.5 (Modèle RL + ARIMA) |
| `GET /alerte/{ville}` | GET | Indice & Alertes | Retounre l'Indice de Risque Sanitaire (IRS) basé sur la méthode PCA et les recommandations paramétradas (OMS AQG 2021) |
| `GET /national` | GET | Statistiques Globales | Synthèse de l'état du Cameroun entier |

---

## 🏗️ Architecture du module

```
api/
│
└── main.py                 # Instance de l'application FastAPI, définition des routes et Middleware CORS.
```

*(L'API s'inspire du dossier global `data/` pour le chargement du `.parquet` et de `models/` pour le re-calcul d'inférence en vol).*

---

## 🚀 Déploiement et Lancement

### Lancer l'API en local

L'exécution locale instancie Uvicorn et permet des requêtes croisées (CORS) avec le Dashboard.
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
Puis accédez à l'interface Swagger **interactive** pour tester manuellement : [http://localhost:8000/docs](http://localhost:8000/docs)

### Déploiement en Production
Le système est actuellement déployé en production via l'environnement "Web Service" de **Render**. Render attache automatiquement l'application au port dynamique `${PORT}` via Uvicorn (Voir fichier `deployment/render.yaml` et le `Dockerfile` à la racine principale).
