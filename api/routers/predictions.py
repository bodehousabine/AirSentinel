"""
api/routers/predictions.py

Endpoints de prédiction ML AirSentinel.
"""

import pandas as pd
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.services.data_service import get_dataframe
from api.services.irs_service import compute_irs
from api.schemas.prediction import IRSInput, IRSResponse, PredictionPoint

router = APIRouter(prefix="/predictions", tags=["Prédictions"])


class MonthlyPM25(BaseModel):
    annee: int
    mois: int
    pm25_moyen: float


# ─── Helpers ───────────────────────────────────────────────────────
def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


# ─── Endpoints ─────────────────────────────────────────────────────
@router.get("/short-term", response_model=list[PredictionPoint])
def get_short_term():
    """
    Retourne :
    - 21 jours d'historique observés
    - 3 jours simulés de prédiction (à remplacer par une vraie prédiction via meilleur_modele.joblib)

    TODO: Passer la prédiction réelle via get_model("modele").predict(features)
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5"])
    if not pm25_col or "date" not in df.columns:
        raise HTTPException(status_code=500, detail="Colonnes 'pm25' ou 'date' absentes du dataset.")

    df_sorted = df.sort_values("date").dropna(subset=[pm25_col])
    last_date = df_sorted["date"].max()

    # Historique : 21 derniers jours en agrégat journalier
    start_hist = last_date - timedelta(days=21)
    hist = (
        df_sorted[df_sorted["date"] >= start_hist]
        .resample("D", on="date")[pm25_col]
        .mean()
        .dropna()
        .reset_index()
    )
    result = [
        PredictionPoint(date=str(row["date"].date()), pm25=round(float(row[pm25_col]), 2))
        for _, row in hist.iterrows()
    ]

    # Prédiction simulée : moyenne glissante des 7 derniers jours ± bruit
    pm25_base = hist[pm25_col].tail(7).mean() if len(hist) >= 7 else hist[pm25_col].mean()
    for i in range(1, 4):
        pred_date = last_date + timedelta(days=i)
        pred_val = round(float(pm25_base) * (1 + 0.02 * i), 2)  # TODO: remplacer par le vrai modèle
        result.append(PredictionPoint(date=str(pred_date.date()), pm25=pred_val, is_prediction=True))

    return result


@router.get("/monthly", response_model=list[MonthlyPM25])
def get_monthly():
    """
    PM2.5 mensuel moyen par année et mois.
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5"])
    if not pm25_col or "date" not in df.columns:
        raise HTTPException(status_code=500, detail="Colonnes 'pm25' ou 'date' absentes du dataset.")

    df["_annee"] = df["date"].dt.year
    df["_mois"] = df["date"].dt.month

    grouped = (
        df.groupby(["_annee", "_mois"])[pm25_col]
        .mean()
        .reset_index()
        .rename(columns={"_annee": "annee", "_mois": "mois", pm25_col: "pm25_moyen"})
        .sort_values(["annee", "mois"])
    )

    return [
        MonthlyPM25(annee=int(r.annee), mois=int(r.mois), pm25_moyen=round(float(r.pm25_moyen), 2))
        for _, r in grouped.iterrows()
    ]


@router.post("/simulate-irs", response_model=IRSResponse)
def simulate_irs(payload: IRSInput):
    """
    Reçoit des paramètres météo et retourne l'IRS simulé via irs_service.compute_irs().
    """
    try:
        result = compute_irs(payload.model_dump(exclude_none=True))
    except (ValueError, FileNotFoundError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    return IRSResponse(**result)
