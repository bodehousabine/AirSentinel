# 🧩 Blocs Analytiques (Dashboard)

> **Composants modulaires interactifs constituant le moteur d'affichage du Dashboard d'AirSentinel**

[![Streamlit Components](https://img.shields.io/badge/Streamlit-Components-red?logo=streamlit)](https://streamlit.io)
[![Plotly Graphs](https://img.shields.io/badge/Plotly-Interactive-blueviolet?logo=plotly)](https://plotly.com)

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Architecture Modulaire (Blocs)](#-architecture-modulaire-blocs)
- [Intégration et Extensibilité](#-intégration-et-extensibilité)

---

## 🎯 À propos

Le répertoire `/blocs` est le cœur analytique de l'interface Streamlit. Au lieu de surcharger un fichier `app.py` monolithe (ce qui devient très vite ingérable pour 5+ pages dynamiques complexes avec du machine learning embarqué), nous avons conçu chaque fonctionnalité majeure comme un "Bloc" autonome et importable. 

Chaque fichier python dans ce dossier contient obligatoirement une fonction standardisée `render(profil)` qui est appelée de manière dynamique par le script central du dashboard en fonction de l'onglet sélectionné.

---

## ✨ Architecture Modulaire (Blocs)

| Fichier | Nom du Composant | Description |
|---|---|---|
| `bloc1_carte.py` | **Cartographie & Régions** | Rendus mapbox via Plotly. Affichage géographique des seuils PM2.5. Toggle pour visionner l'historique ou les prédictions du Jour-J. |
| `bloc2_kpis.py` | **Indicateurs Nationaux** | Focus sur les chiffres macroscopiques (Total des alertes, Polluant Dominant via Pie Chart, Tendances mensuelles lissées). |
| `bloc3_predictions.py`| **Prédictions & Simulations**| Projection ARIMA sur les 72 prochaines heures. Dispose d'un **Simulateur Météorologique** permettant de modifier virtuellement le climat pour anticiper le pic PM2.5. |
| `bloc4_alertes.py` | **Système d'Alerte** | Mappage exact sur les pourcentages d'excès des seuils de l'Organisation Mondiale de la Santé (AQG 2021). |
| `bloc5_decision.py` | **Décision & Export** | Founit des recommandations par types de citoyens. Permet de générer un **Rapport Analytique en PDF** à la volée. |
| `bloc6_shap.py` | **Explicabilité (SHAP)**| Profil climatique par zone (Équatoriale, Soudanienne, Soudano-sahélienne) et impact des variables exogènes sur le modèle (Explicabilité IA Locale et Globale). |

---

## 🏗️ Intégration et Extensibilité

Si un ingénieur de données veut rajouter une analyse de capteur dans le futur (ex: Humidité pure), il lui suffit de :
1. Créer un fichier `bloc7_humidite.py`.
2. Encapsuler sa structure Streamlit dans `def render(profil):`.
3. L'ajouter à l'import dans la racine `app.py`.

*Grâce à cette approche, tous les calculs analytiques de Data Science sont encapsulés et séparés de la logique purement visuelle (UI).*
