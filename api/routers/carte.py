"""
api/routers/carte.py

Endpoints GET /carte et GET /carte/analyses.
Données géolocalisées par ville + 6 analyses enrichies.
"""

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.services.data_service import get_dataframe

router = APIRouter(prefix="/carte", tags=["Carte"])


# ─── Schémas inline ────────────────────────────────────────────────
class VillePoint(BaseModel):
    city: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    pm25_moyen: float
    irs_moyen: Optional[float] = None
    irs_label: Optional[str] = None
    irs_color: Optional[str] = None

class CarteAnalyses(BaseModel):
    pm25_par_region: dict
    tendance_12_mois: dict
    top_3_polluants: list[dict]
    top_5_villes_critiques: list[dict]
    episodes_pollution: int
    pct_depassement_oms: float


# ─── Helpers ───────────────────────────────────────────────────────
def _find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def _irs_label_color(irs_val, status_label=None):
    """
    Détermine le label et la couleur. 
    Priorise le label textuel s'il contient des mots clés ou emojis.
    """
    if status_label:
        l = status_label.upper()
        if "FAIBLE" in l or "🟢" in l:
            return "FAIBLE", "#4CAF50"
        if "MODÉRÉ" in l or "🟡" in l:
            return "MODÉRÉ", "#FFC107"
        if "ÉLEVÉ" in l or "🟠" in l:
            return "ÉLEVÉ", "#FF5722"
        if "CRITIQUE" in l or "🔴" in l:
            return "CRITIQUE", "#B71C1C"

    # Fallback sur les seuils numériques si pas de label
    if irs_val is None:
        return "N/A", "#9E9E9E"
    
    if irs_val <= 0.2:
        return "FAIBLE", "#4CAF50"
    elif irs_val <= 0.5:
        return "MODÉRÉ", "#FFC107"
    elif irs_val <= 0.8:
        return "ÉLEVÉ", "#FF5722"
    else:
        return "CRITIQUE", "#B71C1C"


# ─── Endpoints ─────────────────────────────────────────────────────
@router.get("", response_model=list[VillePoint])
def get_carte():
    """
    Retourne une liste de points géolocalisés par ville avec PM2.5 et IRS.
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    city_col   = _find_col(df, ["ville", "city"])
    pm25_col   = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5"])
    lat_col    = _find_col(df, ["latitude", "lat"])
    lon_col    = _find_col(df, ["longitude", "lon", "lng"])
    irs_col    = _find_col(df, ["IRS", "irs", "irs_value"])
    status_col = _find_col(df, ["niveau_sanitaire", "niveau_alerte", "label"])

    if not city_col:
        raise HTTPException(status_code=500, detail="Colonne ville introuvable.")

    agg = {pm25_col: "mean"} if pm25_col else {}
    if irs_col: agg[irs_col] = "mean"
    if lat_col: agg[lat_col] = "first"
    if lon_col: agg[lon_col] = "first"
    if status_col: agg[status_col] = "first"

    grouped = df.groupby(city_col).agg(agg).reset_index()

    result = []
    for _, row in grouped.iterrows():
        irs_val = float(row[irs_col]) if irs_col else None
        status_text = str(row[status_col]) if status_col else None
        
        label, color = _irs_label_color(irs_val, status_text)
        
        result.append(VillePoint(
            city=row[city_col],
            lat=float(row[lat_col]) if lat_col else None,
            lon=float(row[lon_col]) if lon_col else None,
            pm25_moyen=round(float(row[pm25_col]), 2) if pm25_col else 0.0,
            irs_moyen=round(irs_val, 4) if irs_val is not None else None,
            irs_label=label,
            irs_color=color,
        ))
    return result


@router.get("/analyses", response_model=CarteAnalyses)
def get_analyses():
    """
    Retourne 6 analyses enrichies :
    1. PM2.5 moyen par région
    2. Tendance 12 mois (nationale)
    3. Top 3 polluants disponibles dans le dataset
    4. Top 5 villes critiques (PM2.5 le plus élevé)
    5. Nombre d'épisodes de pollution (jours > seuil)
    6. % de jours dépassant les normes OMS (PM2.5 > 10 µg/m³)
    """
    try:
        df = get_dataframe()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    pm25_col   = _find_col(df, ["pm2_5_moyen", "pm2_5", "pm25", "PM2.5", "PM25"])
    region_col = _find_col(df, ["region", "Region", "Area"])
    city_col   = _find_col(df, ["ville", "city", "Ville", "City"])

    # 1. PM2.5 par région
    pm25_par_region = {}
    if region_col and pm25_col:
        pm25_par_region = df.groupby(region_col)[pm25_col].mean().round(2).to_dict()

    # 2. Tendance 12 mois
    tendance_12_mois = {}
    if "date" in df.columns and pm25_col:
        df_s = df.sort_values("date")
        last12 = df_s[df_s["date"] >= df_s["date"].max() - pd.DateOffset(months=12)]
        monthly = last12.resample("ME", on="date")[pm25_col].mean().round(2)
        tendance_12_mois = {str(k.date()): v for k, v in monthly.items()}

    # 3. Top 3 polluants
    polluant_cols = {
        "PM2.5": _find_col(df, ["pm2_5", "pm25"]),
        "PM10":  _find_col(df, ["pm10"]),
        "NO2":   _find_col(df, ["no2"]),
        "O3":    _find_col(df, ["o3"]),
        "SO2":   _find_col(df, ["so2"]),
    }
    available = {k: round(float(df[v].mean()), 2) for k, v in polluant_cols.items() if v}
    top_3 = sorted(available.items(), key=lambda x: x[1], reverse=True)[:3]
    top_3_polluants = [{"polluant": k, "moyenne": v} for k, v in top_3]

    # 4. Top 5 villes critiques
    top_5_villes = []
    if city_col and pm25_col:
        city_means = df.groupby(city_col)[pm25_col].mean().sort_values(ascending=False)
        top_5 = city_means.head(5)
        top_5_villes = [{"city": c, "pm25_moyen": round(v, 2)} for c, v in top_5.items()]

    # 5. Épisodes de pollution (journées > OMS de 25 µg/m³)
    seuil_episode = 25.0
    episodes = 0
    if pm25_col and "date" in df.columns:
        daily = df.resample("D", on="date")[pm25_col].mean()
        episodes = int((daily > seuil_episode).sum())

    # 6. % dépassement OMS (10 µg/m³)
    pct_oms = 0.0
    if pm25_col:
        pct_oms = round(float((df[pm25_col] > 10).mean() * 100), 2)

    return CarteAnalyses(
        pm25_par_region=pm25_par_region,
        tendance_12_mois=tendance_12_mois,
        top_3_polluants=top_3_polluants,
        top_5_villes_critiques=top_5_villes,
        episodes_pollution=episodes,
        pct_depassement_oms=pct_oms,
    )
