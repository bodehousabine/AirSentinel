"""
api/routers/alertes.py

Endpoint GET /alertes — Distribution des jours par niveau IRS par année.
"""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.data_service import get_dataframe

router = APIRouter(prefix="/alertes", tags=["Alertes"])


class AlerteAnneeLevels(BaseModel):
    FAIBLE: int = 0
    MODÉRÉ: int = 0
    ÉLEVÉ: int = 0
    CRITIQUE: int = 0


def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _classify_pm25(val: float) -> str:
    """
    Classification par niveau IRS basée sur PM2.5 (en µg/m³) selon l'OMS.
    TODO: Remplacer par la vraie classification IRS via irs_service si le score IRS existe dans le CSV.
    """
    if val <= 10:
        return "FAIBLE"
    elif val <= 25:
        return "MODÉRÉ"
    elif val <= 50:
        return "ÉLEVÉ"
    else:
        return "CRITIQUE"


@router.get("", response_model=dict[str, AlerteAnneeLevels])
def get_alertes():
    """
    Retourne la distribution des jours par niveau IRS pour chaque année.
    La clé est l'année (ex: "2022"), la valeur est le décompte par niveau.
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    pm25_col = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5"])
    irs_col  = _find_col(df, ["IRS", "irs", "irs_value"])

    if "date" not in df.columns:
        raise HTTPException(status_code=500, detail="Colonne 'date' absente du dataset.")

    # Agréger par jour pour avoir une valeur journalière
    agg_col = irs_col if irs_col else pm25_col
    if not agg_col:
        raise HTTPException(status_code=500, detail="Aucune colonne IRS ou PM2.5 trouvée.")

    daily = df.resample("D", on="date")[agg_col].mean().dropna().reset_index()
    daily["_annee"] = daily["date"].dt.year

    # Classer chaque journée
    if irs_col:
        # Si IRS numérique disponible, classifier par seuils numériques bruts
        seuils = daily[agg_col].quantile([0.50, 0.75, 0.90]).to_dict()
        def classify_irs(val):
            if val <= seuils[0.50]:
                return "FAIBLE"
            elif val <= seuils[0.75]:
                return "MODÉRÉ"
            elif val <= seuils[0.90]:
                return "ÉLEVÉ"
            else:
                return "CRITIQUE"
        daily["_niveau"] = daily[agg_col].apply(classify_irs)
    else:
        daily["_niveau"] = daily[agg_col].apply(_classify_pm25)

    result = {}
    for annee, grp in daily.groupby("_annee"):
        counts = grp["_niveau"].value_counts().to_dict()
        result[str(annee)] = AlerteAnneeLevels(
            FAIBLE=counts.get("FAIBLE", 0),
            MODÉRÉ=counts.get("MODÉRÉ", 0),
            ÉLEVÉ=counts.get("ÉLEVÉ", 0),
            CRITIQUE=counts.get("CRITIQUE", 0),
        )
    return result
