# 📱 Progressive Web App (PWA) AirSentinel

> **Interface "Grand public" ultra-légère installable sur téléphone permettant un suivi hors-ligne de l'Indice Sanitaire**

[![HTML5](https://img.shields.io/badge/HTML5-E34F26-orange?logo=html5)](https://w3.org)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6-blue?logo=css3)](https://w3.org)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E-yellow?logo=javascript)](https://js.org)
[![Render](https://img.shields.io/badge/Static_Site-Render-black?logo=render)](https://render.com)

---

## 📋 Table des matières

- [À propos](#-à-propos)
- [Fonctionnalités Clés](#-fonctionnalités-clés)
- [Architecture PWA](#-architecture-pwa)
- [Installation Native de l'App](#-installation-native-de-lapp)

---

## 🎯 À propos

Ce sous-projet régit la **PWA (Progressive Web App)** d'AirSentinel. Conçue de zéro sans framework lourd (pas de React ou Vue), elle est optimisée pour se charger extrêmement vite dans le contexte réseau camerounais avec des technologies pures (Vanilla JS/HTML5). L'interface mobile dialogue de façon asynchrone par `fetch()` au backend FastAPI distant.

---

## ✨ Fonctionnalités Clés

| Fonctionnalité | Description |
|---|---|
| 📉 **Catégorisation Chromatique** | UI ajustant dynamiquement ses couleurs avec précision (`--status-X` variables) envers les exigences 2021 de la qualité de l'Air OMS. |
| 🛡️ **Offline-First** | Mise à disposition des données pré-téléchargées en mode hors-connexion. |
| 📌 **Application Native** | Bannière invitant à "l'installation App" sans aucun passage sur Play Store/App Store, conférant une icône native et une présentation plein-écran (Standalone). |
| 🌍 **Carte Asynchrone** | Intégration de `leaflet.js` pour une expérience dynamique des 40 villes sur la cartographie Open-Street Maps. |

---

## 🏗️ Architecture PWA

```
pwa/
│
├── index.html              # Fichier central (HTML layout + Logique JS intégrée)
├── sw.js                   # Service Worker (Cache de requêtes fetch API et ressources UI)
├── manifest.json           # Méthadonnées WebApp (couleurs, orientation forcée, icônes)
└── logo.jpg                # Logo 512x512 pour ancrage Android/iOS
```

---

## 🚀 Installation Native de l'App

Le dossier a été pensé pour le déploiement en tant que "Site Statique" pur sur Render, GitHub pages ou Vercel.

**Pour le visiteur final :**
1. Visiter l'URL publique générée via un simple Navigateur Mobile (ex: Safari ou Chrome).
2. Cliquer sur la proposition pop-up ou le menu `Ajouter à l'écran d'accueil`.
3. L'application place le logo AirSentinel près des applications usuelles de l'utilisateur, opérant sans trace visuelle de navigateur ni barre de recherche !
