---
title: AirSentinel API
emoji: 🌬️
colorFrom: blue
colorTo: sky
sdk: docker
app_port: 7860
pinned: false
---

# 🌍 AirSentinel Cameroun
Système IA de prédiction qualité air — IndabaX 2026
Ce projet est conçu pour apporter des solutions technologiques concrètes et  innovantes aux défis de notre environnement. 

## Équipe DPA Green Tech
- BODEHOU Sabine (ISSEA) — Data Science
- FANKAM Marc Aurel (ISSEA) — Modélisation
- PEURBAR RIMBAR Firmin (ISSEA) — SHAP & Rapport
- FOFACK ALEMDJOU Henri Joël (ENSPY) — Frontend & API

## Installation
pip install -r requirements.txt

## Lancer le dashboard
streamlit run dashboard/app.py

## Lancer l'API
uvicorn api.main:app --reload
