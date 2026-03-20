# AirSentinel Cameroun — API FastAPI
# Auteur : Henri Joël — ENSP Yaoundé
from fastapi import FastAPI

app = FastAPI(
    title="AirSentinel API",
    description="Prédiction qualité air Cameroun",
    version="1.0.0"
)

@app.get("/")
def accueil():
    return {
        "projet": "AirSentinel Cameroun",
        "equipe": "DPA Green Tech",
        "hackathon": "IndabaX Cameroon 2026"
    }
