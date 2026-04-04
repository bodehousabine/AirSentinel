"""
=============================================================================
 AirSentinel Cameroun — Équipe DPA Green Tech
=============================================================================
 SCRIPT : api.py
 API publique FastAPI — Prédictions qualité de l'air · 40 villes

 UTILISATION :
   uvicorn api:app --reload --host 0.0.0.0 --port 8000

 DOCUMENTATION INTERACTIVE :
   http://localhost:8000/docs
=============================================================================
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta, date
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

VERSION   = "1.0.0"
TITLE     = "AirSentinel Cameroun API"
DESC      = """
## 🌬️ AirSentinel Cameroun — API Publique

Système d'aide à la décision sanitaire basé sur l'IA.
Prédictions PM2.5 pour 40 villes camerounaises · 10 régions · 3 zones climatiques INS (2019)

### Endpoints disponibles
- **/** — Informations sur l'API
- **/villes** — Liste des 40 villes
- **/regions** — Liste des 10 régions
- **/data/{ville}** — Dernières données d'une ville
- **/predict/{ville}** — Prédictions J/J+1/J+2
- **/alerte/{ville}** — Niveau d'alerte + recommandations
- **/national** — Résumé national
- **/historique/{ville}** — Historique PM2.5 d'une ville

### Modèle
Modèle Hybride Régression Linéaire + ARIMA par zone climatique INS Cameroun (2019)
R² = 0.893 · MAE = 3.456 µg/m³ · Données test 2025

### Références
WHO AQG 2021 · NCBI NBK574591 · INS Cameroun (2019) · Chen & Hoek (2020)
"""

app = FastAPI(
    title=TITLE,
    description=DESC,
    version=VERSION,
    contact={
        "name": "DPA Green Tech — IndabaX Cameroon 2026",
        "email": "airsentinel@dpa-greentech.cm",
    },
    license_info={
        "name": "MIT",
    }
)

# CORS — autoriser tous les origines pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# ZONES CLIMATIQUES INS CAMEROUN (2019)
# ─────────────────────────────────────────────────────────────────────────────

ZONES_REGIONS = {
    "Zone équatoriale":        ["Centre", "Est", "Sud", "Littoral", "Sud-Ouest", "Ouest", "Nord-Ouest"],
    "Zone soudanienne":        ["Adamaoua", "Nord"],
    "Zone soudano-sahélienne": ["Extreme-Nord"],
}

# Seuils OMS AQG 2021 — NCBI NBK574591
SEUILS = {
    "AQG": 15.0,
    "IT4": 25.0,
    "IT3": 37.5,
    "IT2": 50.0,
    "IT1": 75.0,
}

# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DES DONNÉES ET MODÈLES
# ─────────────────────────────────────────────────────────────────────────────

def _get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))

def _load_dataset():
    """Charge le dataset depuis parquet ou xlsx."""
    base = _get_base_dir()
    chemins = [
        os.path.join(base, "data", "processed", "dataset_final.parquet"),
        os.path.join(base, "..", "data", "processed", "dataset_final.parquet"),
    ]
    for chemin in chemins:
        if os.path.exists(chemin):
            df = pd.read_parquet(chemin)
            df["date"] = pd.to_datetime(df["date"])
            return df
    raise FileNotFoundError("Dataset introuvable — vérifier data/processed/dataset_final.parquet")

def _load_models():
    """Charge les modèles ML."""
    base = _get_base_dir()
    chemins = [
        os.path.join(base, "models"),
        os.path.join(base, "..", "models"),
    ]
    for chemin in chemins:
        pkl = os.path.join(chemin, "meilleur_modele.pkl")
        if os.path.exists(pkl):
            return {
                "modele":   joblib.load(os.path.join(chemin, "meilleur_modele.pkl")),
                "scaler":   joblib.load(os.path.join(chemin, "scaler.pkl")),
                "features": joblib.load(os.path.join(chemin, "features.pkl")),
                "arima":    joblib.load(os.path.join(chemin, "arima_par_zone.pkl")),
            }
    return None

# Chargement au démarrage
try:
    DF     = _load_dataset()
    MODELS = _load_models()
    print(f"✅ Dataset chargé : {len(DF):,} lignes · {DF['date'].max().date()}")
    print(f"✅ Modèles : {'chargés' if MODELS else 'non disponibles'}")
except Exception as e:
    print(f"❌ Erreur chargement : {e}")
    DF     = None
    MODELS = None

# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────────────────────

def _get_zone(region: str) -> str:
    for zone, regions in ZONES_REGIONS.items():
        if region in regions:
            return zone
    return "Zone équatoriale"

def _get_niveau(pm25: float) -> dict:
    """Retourne le niveau de risque OMS pour une valeur PM2.5."""
    if   pm25 <= SEUILS["AQG"]: niveau, code = "FAIBLE",     0
    elif pm25 <= SEUILS["IT4"]: niveau, code = "MODÉRÉ",     1
    elif pm25 <= SEUILS["IT3"]: niveau, code = "ÉLEVÉ",      2
    elif pm25 <= SEUILS["IT2"]: niveau, code = "TRÈS ÉLEVÉ", 3
    elif pm25 <= SEUILS["IT1"]: niveau, code = "CRITIQUE",   4
    else:                        niveau, code = "DANGEREUX",  5
    return {
        "niveau":      niveau,
        "code":        code,
        "seuil_oms":   SEUILS["AQG"],
        "ratio_oms":   round(pm25 / SEUILS["AQG"], 2),
        "conforme_oms": pm25 <= SEUILS["AQG"],
    }

def _predire_ville(ville: str, steps: int = 3) -> list:
    """Prédit PM2.5 pour une ville sur N jours."""
    if DF is None or MODELS is None:
        return []

    df_v = DF[DF["ville"] == ville].sort_values("date")
    if len(df_v) == 0:
        return []

    region = df_v["region"].iloc[-1]
    zone   = _get_zone(region)

    preds = []
    for step in range(1, steps + 1):
        try:
            features = MODELS["features"]
            last     = df_v[features].fillna(df_v[features].median()).tail(1)
            last_s   = MODELS["scaler"].transform(last)
            p_rl     = MODELS["modele"].predict(last_s)[0]
            p_arima  = MODELS["arima"][zone].forecast(steps=step).iloc[-1]
            preds.append(max(0, round(float(p_rl + p_arima), 2)))
        except:
            base = float(df_v["pm2_5_moyen"].mean())
            preds.append(round(base, 2))
    return preds

def _check_ville(ville: str):
    """Vérifie que la ville existe dans le dataset."""
    if DF is None:
        raise HTTPException(status_code=503, detail="Dataset non disponible")
    villes = DF["ville"].unique().tolist()
    if ville not in villes:
        raise HTTPException(
            status_code=404,
            detail=f"Ville '{ville}' introuvable. Villes disponibles : {sorted(villes)}"
        )

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    """Informations générales sur l'API AirSentinel."""
    return {
        "nom":         "AirSentinel Cameroun API",
        "version":     VERSION,
        "description": "Système d'aide à la décision sanitaire · Qualité de l'air",
        "equipe":      "DPA Green Tech — IndabaX Cameroon 2026",
        "membres":     ["BODEHOU Sabine", "FANKAM Marc Aurel", "PEURBAR Firmin", "FOFACK Henri Joël"],
        "modele":      "Hybride Régression Linéaire + ARIMA par zone climatique INS (2019)",
        "performances": {"r2": 0.893, "mae": 3.456, "unite": "µg/m³"},
        "donnees": {
            "villes":       40,
            "regions":      10,
            "zones":        3,
            "periode":      f"{DF['date'].min().date()} → {DF['date'].max().date()}" if DF is not None else "N/A",
            "observations": len(DF) if DF is not None else 0,
        },
        "references": [
            "WHO AQG 2021 · NCBI NBK574591",
            "INS Cameroun (2019)",
            "Chen & Hoek (2020)",
        ],
        "docs": "/docs",
    }


@app.get("/villes", tags=["Données"])
def liste_villes():
    """Retourne la liste des 40 villes disponibles avec leurs coordonnées."""
    if DF is None:
        raise HTTPException(status_code=503, detail="Dataset non disponible")

    villes = (
        DF.drop_duplicates("ville")[["ville", "region", "latitude", "longitude"]]
        .sort_values("ville")
        .to_dict(orient="records")
    )
    # Ajouter zone climatique
    for v in villes:
        v["zone"] = _get_zone(v["region"])

    return {
        "count":  len(villes),
        "villes": villes,
    }


@app.get("/regions", tags=["Données"])
def liste_regions():
    """Retourne la liste des 10 régions avec leurs zones climatiques."""
    if DF is None:
        raise HTTPException(status_code=503, detail="Dataset non disponible")

    regions = []
    for region in sorted(DF["region"].unique()):
        villes_region = DF[DF["region"] == region]["ville"].unique().tolist()
        regions.append({
            "region": region,
            "zone":   _get_zone(region),
            "villes": sorted(villes_region),
            "nb_villes": len(villes_region),
        })
    return {
        "count":   len(regions),
        "regions": regions,
    }


@app.get("/data/{ville}", tags=["Données"])
def donnees_ville(
    ville: str,
    jours: int = Query(default=7, ge=1, le=90, description="Nombre de jours d'historique")
):
    """Retourne les dernières données d'une ville (PM2.5, météo, IRS...)."""
    _check_ville(ville)

    df_v = DF[DF["ville"] == ville].sort_values("date").tail(jours)

    cols = ["date", "ville", "region", "pm2_5_moyen", "pm2_5_max",
            "IRS", "niveau_sanitaire", "polluant_dominant",
            "temperature_2m_max", "wind_speed_10m_max",
            "precipitation_sum", "dust_moyen", "us_aqi_moyen"]
    cols_ok = [c for c in cols if c in df_v.columns]
    df_out  = df_v[cols_ok].copy()
    df_out["date"] = df_out["date"].dt.strftime("%Y-%m-%d")

    derniere = df_out.iloc[-1].to_dict() if len(df_out) > 0 else {}
    pm25_last = float(df_v["pm2_5_moyen"].iloc[-1]) if len(df_v) > 0 else 0

    return {
        "ville":        ville,
        "region":       df_v["region"].iloc[0] if len(df_v) > 0 else "",
        "zone":         _get_zone(df_v["region"].iloc[0]) if len(df_v) > 0 else "",
        "derniere_date": str(df_v["date"].max().date()) if len(df_v) > 0 else "",
        "pm25_actuel":  round(pm25_last, 2),
        "niveau":       _get_niveau(pm25_last),
        "historique":   df_out.to_dict(orient="records"),
    }


@app.get("/predict/{ville}", tags=["Prédictions"])
def predire_ville(ville: str):
    """
    Prédit PM2.5 pour une ville sur 3 jours (J/J+1/J+2).

    Modèle : Hybride Régression Linéaire + ARIMA
    R² = 0.893 · MAE = 3.456 µg/m³ · IC = ±3.456 µg/m³
    """
    _check_ville(ville)

    df_v   = DF[DF["ville"] == ville].sort_values("date")
    region = df_v["region"].iloc[-1] if len(df_v) > 0 else "Centre"
    zone   = _get_zone(region)
    preds  = _predire_ville(ville, steps=3)

    if not preds:
        raise HTTPException(status_code=500, detail="Erreur lors de la prédiction")

    MAE = 3.456
    jours_lbl = ["Aujourd'hui", "Demain", "Après-demain"]
    predictions = []
    for i, (lbl, pred) in enumerate(zip(jours_lbl, preds)):
        jour = date.today() + timedelta(days=i)
        predictions.append({
            "jour":          i,
            "label":         lbl,
            "date":          str(jour),
            "pm25_predit":   pred,
            "pm25_min":      round(max(0, pred - MAE), 2),
            "pm25_max":      round(pred + MAE, 2),
            "ic":            f"±{MAE} µg/m³",
            "niveau":        _get_niveau(pred),
        })

    return {
        "ville":       ville,
        "region":      region,
        "zone":        zone,
        "predictions": predictions,
        "modele": {
            "nom":  "Hybride RL+ARIMA",
            "zone": zone,
            "r2":   0.893,
            "mae":  MAE,
            "ref":  "INS Cameroun (2019) · Box & Jenkins (1976)",
        },
    }


@app.get("/alerte/{ville}", tags=["Alertes"])
def alerte_ville(ville: str):
    """
    Retourne le niveau d'alerte actuel et les recommandations pour une ville.

    Recommandations adaptées aux profils : citoyen, médecin, maire, chercheur.
    """
    _check_ville(ville)

    df_v   = DF[DF["ville"] == ville].sort_values("date")
    date_max = df_v["date"].max()
    df_jour  = df_v[df_v["date"] == date_max]

    pm25   = float(df_jour["pm2_5_moyen"].mean()) if len(df_jour) > 0 else float(df_v["pm2_5_moyen"].mean())
    niveau = _get_niveau(pm25)
    snk    = niveau["code"]

    # Recommandations par profil
    reco_map = {
        0: {  # FAIBLE
            "citoyen":    "Qualité de l'air satisfaisante. Activités normales autorisées.",
            "medecin":    "Pas d'alerte sanitaire. Surveillance de routine suffisante.",
            "maire":      "Situation normale. Aucune mesure d'urgence requise.",
            "chercheur":  "Données conformes aux seuils OMS AQG 2021. Niveau de base.",
        },
        1: {  # MODÉRÉ
            "citoyen":    "Réduire les activités intenses en extérieur. Porter un masque en cas de gêne.",
            "medecin":    "Surveiller les patients sensibles. Anticiper hausse des consultations.",
            "maire":      "Diffuser des recommandations préventives. Surveiller l'évolution.",
            "chercheur":  "Dépassement IT4 (25 µg/m³). Analyser les sources d'émission locales.",
        },
        2: {  # ÉLEVÉ
            "citoyen":    "Limiter les sorties. Fermer les fenêtres. Éviter l'effort physique.",
            "medecin":    "Alerter les patients asthmatiques. Renforcer stocks d'inhalateurs.",
            "maire":      "Déclencher une alerte publique. Réduire sources de pollution locales.",
            "chercheur":  "Dépassement IT3 (37.5 µg/m³). Identifier l'épisode climatique en cours.",
        },
        3: {  # TRÈS ÉLEVÉ
            "citoyen":    "Eviter toute sortie non essentielle. Masque obligatoire.",
            "medecin":    "Renforcer urgences respiratoires. Protocole asthme activé.",
            "maire":      "Alertes SMS publiques. Fermeture activités extérieures scolaires.",
            "chercheur":  "Dépassement IT2 (50 µg/m³). Analyser corrélation dust/harmattan.",
        },
        4: {  # CRITIQUE
            "citoyen":    "DANGER — Rester confiné. Consulter un médecin si symptômes.",
            "medecin":    "URGENCE — Activer protocole urgence respiratoire.",
            "maire":      "CRISE — Plan d'urgence sanitaire. Alertes obligatoires.",
            "chercheur":  "Dépassement IT1 (75 µg/m³). Documenter et analyser l'épisode.",
        },
        5: {  # DANGEREUX
            "citoyen":    "DANGER EXTRÊME — Ne pas sortir. Appeler le 15 si crise.",
            "medecin":    "URGENCE MAXIMALE — Toutes ressources médicales mobilisées.",
            "maire":      "CATASTROPHE SANITAIRE — Déclencher plan national d'urgence.",
            "chercheur":  "Pic exceptionnel. Documenter immédiatement. Alerter autorités.",
        },
    }

    return {
        "ville":       ville,
        "region":      df_v["region"].iloc[0] if len(df_v) > 0 else "",
        "zone":        _get_zone(df_v["region"].iloc[0]) if len(df_v) > 0 else "",
        "date":        str(date_max.date()),
        "pm25":        round(pm25, 2),
        "niveau":      niveau,
        "recommandations": reco_map.get(snk, reco_map[0]),
        "populations_vulnerables": {
            "enfants":    "Réduire activités extérieures" if snk >= 1 else "Activités normales",
            "enceintes":  "Limiter sorties prolongées"    if snk >= 1 else "Sorties normales",
            "ages":       "Éviter efforts en extérieur"   if snk >= 1 else "Activité légère possible",
            "asthmatiques": "Avoir bronchodilatateur"     if snk >= 1 else "Surveillance normale",
            "agriculteurs": "Porter masque FFP2"          if snk >= 1 else "Travaux sans restriction",
        },
        "ref": "WHO AQG 2021 · NCBI NBK574591 · Chen & Hoek (2020)",
    }


@app.get("/national", tags=["Données"])
def resume_national():
    """Résumé national de la qualité de l'air au Cameroun."""
    if DF is None:
        raise HTTPException(status_code=503, detail="Dataset non disponible")

    date_max = DF["date"].max()
    df_jour  = DF[DF["date"] == date_max]

    # Stats par ville
    pm25_par_ville = df_jour.groupby("ville")["pm2_5_moyen"].mean().sort_values(ascending=False)
    top5_critiques = pm25_par_ville.head(5).reset_index().to_dict(orient="records")
    top5_saines    = pm25_par_ville.tail(5).reset_index().to_dict(orient="records")

    # Stats par région
    pm25_par_region = df_jour.groupby("region")["pm2_5_moyen"].mean().sort_values(ascending=False)

    pm25_national = float(df_jour["pm2_5_moyen"].mean())
    n_villes_oms  = int((pm25_par_ville > SEUILS["AQG"]).sum())

    return {
        "date":            str(date_max.date()),
        "pm25_national":   round(pm25_national, 2),
        "niveau_national": _get_niveau(pm25_national),
        "villes_total":    int(df_jour["ville"].nunique()),
        "villes_dessus_oms": n_villes_oms,
        "pct_dessus_oms":  round(n_villes_oms / df_jour["ville"].nunique() * 100, 1),
        "top5_critiques":  [{"ville": r["ville"], "pm25": round(r["pm2_5_moyen"], 2)} for r in top5_critiques],
        "top5_saines":     [{"ville": r["ville"], "pm25": round(r["pm2_5_moyen"], 2)} for r in top5_saines],
        "par_region":      {r: round(float(v), 2) for r, v in pm25_par_region.items()},
        "ref":             "WHO AQG 2021 · INS Cameroun (2019)",
    }


@app.get("/historique/{ville}", tags=["Données"])
def historique_ville(
    ville: str,
    debut: Optional[str] = Query(default=None, description="Date début (YYYY-MM-DD)"),
    fin:   Optional[str] = Query(default=None, description="Date fin (YYYY-MM-DD)"),
    jours: int           = Query(default=30, ge=1, le=365, description="Nb jours si pas de dates")
):
    """Retourne l'historique PM2.5 d'une ville."""
    _check_ville(ville)

    df_v = DF[DF["ville"] == ville].sort_values("date")

    if debut and fin:
        df_v = df_v[(df_v["date"] >= debut) & (df_v["date"] <= fin)]
    else:
        df_v = df_v.tail(jours)

    cols   = ["date", "pm2_5_moyen", "IRS", "niveau_sanitaire", "polluant_dominant"]
    cols_ok = [c for c in cols if c in df_v.columns]
    df_out  = df_v[cols_ok].copy()
    df_out["date"] = df_out["date"].dt.strftime("%Y-%m-%d")

    return {
        "ville":     ville,
        "region":    DF[DF["ville"] == ville]["region"].iloc[0],
        "zone":      _get_zone(DF[DF["ville"] == ville]["region"].iloc[0]),
        "periode":   f"{df_out['date'].min()} → {df_out['date'].max()}" if len(df_out) > 0 else "",
        "nb_jours":  len(df_out),
        "pm25_moy":  round(float(df_v["pm2_5_moyen"].mean()), 2),
        "pm25_max":  round(float(df_v["pm2_5_moyen"].max()), 2),
        "pm25_min":  round(float(df_v["pm2_5_moyen"].min()), 2),
        "historique": df_out.to_dict(orient="records"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# LANCEMENT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)