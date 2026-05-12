"""
utils.py — AirSentinel Cameroun
get_context() avec lang + theme, composants visuels adaptatifs.
OPTIMISÉ : lecture parquet (5-10x plus rapide que xlsx)
"""
import streamlit as st
from streamlit.components.v1 import html as st_html
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib, os, base64, re
from themes import get_theme, THEMES
from translations import get_t
import time

def render_transition_loader(lang="fr", duration=2.5):
    """
    Affiche un écran de transition haute-fidélité (Sentinel Eye + Progress Bar) 
    pour masquer le passage du Landing au Dashboard.
    """
    msg = "Initialisation du Dashboard..." if lang=="fr" else "Initializing Dashboard..."
    anim_duration = duration 
    
    st.markdown(f"""
        <div class="transition-container">
            <div class="sentinel-loader">
                <div class="ring outer"></div>
                <div class="ring middle"></div>
                <div class="core-pulse"></div>
            </div>
            <div class="msg-text">{msg}</div>
            <div class="progress-track">
                <div class="progress-bar"></div>
            </div>
        </div>

        <style>
            .transition-container {{
                position: fixed; inset: 0;
                background: radial-gradient(circle at center, #071e35 0%, #020c18 100%);
                z-index: 1000000;
                display: flex; flex-direction: column;
                justify-content: center; align-items: center;
                font-family: 'Inter', sans-serif;
            }}
            
            .sentinel-loader {{
                position: relative; width: 140px; height: 140px;
                margin-bottom: 50px;
                display: flex; justify-content: center; align-items: center;
            }}
            
            .ring {{
                position: absolute; border-radius: 50%;
                border: 2px solid transparent;
            }}
            
            .outer {{
                width: 130px; height: 130px;
                border-top-color: #00d4b1;
                border-bottom-color: #00d4b1;
                animation: rotate-cw 3s linear infinite;
            }}
            
            .middle {{
                width: 90px; height: 90px;
                border-left-color: #f59e0b;
                border-right-color: #f59e0b;
                animation: rotate-ccw 2s linear infinite;
                opacity: 0.8;
            }}
            
            .core-pulse {{
                width: 45px; height: 45px;
                background: #00d4b1;
                border-radius: 50%;
                box-shadow: 0 0 30px #00d4b188;
                animation: core-glow 1.5s ease-in-out infinite alternate;
            }}
            
            @keyframes rotate-cw {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
            
            @keyframes rotate-ccw {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(-360deg); }}
            }}
            
            @keyframes core-glow {{
                0% {{ transform: scale(0.9); box-shadow: 0 0 15px #00d4b166; }}
                100% {{ transform: scale(1.1); box-shadow: 0 0 45px #00d4b1cc; }}
            }}
            
            .msg-text {{
                color: #00d4b1; font-size: 18px; font-weight: 800;
                margin-bottom: 25px; letter-spacing: 2px;
                text-transform: uppercase;
                text-shadow: 0 0 15px rgba(0, 212, 177, 0.4);
                animation: text-pulse 2s ease-in-out infinite;
            }}
            
            @keyframes text-pulse {{
                0%, 100% {{ opacity: 0.7; }}
                50% {{ opacity: 1; }}
            }}
            
            .progress-track {{
                width: 350px; height: 4px;
                background: rgba(255,255,255,0.08); 
                border-radius: 20px;
                overflow: hidden;
            }}
            
            .progress-bar {{
                width: 0%; height: 100%;
                background: linear-gradient(90deg, #00d4b1, #f59e0b);
                box-shadow: 0 0 10px #00d4b188;
                animation: fill-bar {anim_duration}s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            }}
            
            @keyframes fill-bar {{
                0% {{ width: 0%; }}
                100% {{ width: 100%; }}
            }}
            
            .stApp {{ visibility: hidden !important; }}
        </style>
    """, unsafe_allow_html=True)

def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

MOIS_FR = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
MOIS_EN = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ── 40 villes réelles du dataset ──────────────────────────────────────────────
VILLES = []  # sera chargé dynamiquement depuis le dataset
#
REGIONS = []

POLLUANTS = [
    {"col":"pm2_5_moyen", "nom_fr":"PM2.5",  "nom_en":"PM2.5",  "seuil":15.0,  "unite":"µg/m³", "color":"#f87171"},
    {"col":"pm10_moyen",  "nom_fr":"PM10",   "nom_en":"PM10",   "seuil":45.0,  "unite":"µg/m³", "color":"#fb923c"},
    {"col":"no2_moyen",   "nom_fr":"NO₂",    "nom_en":"NO₂",    "seuil":25.0,  "unite":"µg/m³", "color":"#fbbf24"},
    {"col":"so2_moyen",   "nom_fr":"SO₂",    "nom_en":"SO₂",    "seuil":40.0,  "unite":"µg/m³", "color":"#a78bfa"},
    {"col":"ozone_moyen", "nom_fr":"Ozone",  "nom_en":"Ozone",  "seuil":100.0, "unite":"µg/m³", "color":"#38bdf8"},
    {"col":"co_moyen",    "nom_fr":"CO",     "nom_en":"CO",     "seuil":250.0,  "unite":"µg/m³", "color":"#34d399"},
]

def risk_color(val, seuil, th):
    if val <= seuil:        return th["green"]
    if val <= seuil * 1.5:  return th["amber"]
    if val <= seuil * 2.5:  return th["coral"]
    return                         th["red"]

# ══════════════════════════════════════════════════════════════════════════════
# DONNÉES — lecture parquet (rapide) avec fallback xlsx
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def load_data():
    global VILLES, REGIONS
    import os

    # ── Essai parquet (5-10x plus rapide) ────────────────────────────────
    chemins_parquet = [
        "data/processed/dataset_final.parquet",
        "../data/processed/dataset_final.parquet",
        os.path.join(os.path.dirname(__file__), "../data/processed/dataset_final.parquet"),
    ]
    df = None
    for chemin in chemins_parquet:
        try:
            df = pd.read_parquet(chemin)
            df["date"] = pd.to_datetime(df["date"])
            break
        except Exception:
            continue

    # ── Fallback xlsx si parquet absent ──────────────────────────────────
    if df is None:
        chemins_xlsx = [
            "data/processed/dataset_final.xlsx",
            "../data/processed/dataset_final.xlsx",
            os.path.join(os.path.dirname(__file__), "../data/processed/dataset_final.xlsx"),
        ]
        for chemin in chemins_xlsx:
            try:
                df = pd.read_excel(chemin)
                df["date"] = pd.to_datetime(df["date"])
                break
            except Exception:
                continue

    # ── Données de démo si dataset absent ────────────────────────────────
    if df is None:
        np.random.seed(42)
        dates = pd.date_range("2022-07-01", "2025-12-20", freq="D")
        n = len(dates)
        s = 12 * np.sin(2 * np.pi * np.arange(n) / 365)
        pm = np.clip(18 + s + np.linspace(0, 4, n) + np.random.normal(0, 5, n), 5, 120)
        villes_demo = VILLES[:20]
        df = pd.DataFrame({
            "date":       np.tile(dates, len(villes_demo))[:n * 2][:n],
            "pm2_5_moyen": pm,
            "pm10_moyen":  pm * 1.8 + np.random.normal(0, 3, n),
            "no2_moyen":   15 + np.random.normal(0, 4, n),
            "so2_moyen":   8 + np.random.normal(0, 2, n),
            "co_moyen":    0.6 + np.random.normal(0, 0.1, n),
            "dust_moyen":  pm * 0.6 + np.random.normal(0, 4, n),
            "ozone_moyen": 60 + np.random.normal(0, 8, n),
            "uv_moyen":    7 + 4 * np.sin(2 * np.pi * np.arange(n) / 365),
            "temperature_2m_max":
                28 + 6 * np.sin(2 * np.pi * np.arange(n) / 365) + np.random.normal(0, 2, n),
            "wind_speed_10m_max": 12 + np.random.normal(0, 3, n),
            "us_aqi_moyen": pm * 2.5,
            "ville":   np.random.choice(villes_demo, n),
            "region":  np.random.choice(REGIONS, n),
            "latitude":  np.tile([4.0, 3.8, 4.1], n//3 + 1)[:n],
            "longitude": np.tile([11.5, 12.0, 9.7], n//3 + 1)[:n],
            "polluant_dominant": np.random.choice(
                ["PM2.5", "Dust", "CO", "NO2", "Ozone"], n,
                p=[.45, .25, .15, .10, .05]),
        })

    # ── Calcul IRS si absent ──────────────────────────────────────────────
    if "IRS" not in df.columns:
        try:
            import joblib
            scaler_paths = ["models/scaler_acp_irs.pkl", "../models/scaler_acp_irs.pkl"]
            pca_paths    = ["models/pca_irs.pkl",         "../models/pca_irs.pkl"]
            cols_paths   = ["models/cols_irs.pkl",         "../models/cols_irs.pkl"]
            seuils_paths = ["models/seuils_irs.pkl",       "../models/seuils_irs.pkl"]

            scaler = pca = cols_irs = seuils = None
            for p in scaler_paths:
                if os.path.exists(p): scaler = joblib.load(p); break
            for p in pca_paths:
                if os.path.exists(p): pca = joblib.load(p); break
            for p in cols_paths:
                if os.path.exists(p): cols_irs = joblib.load(p); break
            for p in seuils_paths:
                if os.path.exists(p): seuils = joblib.load(p); break

            if scaler and pca and cols_irs and seuils:
                cols_ok  = [c for c in cols_irs if c in df.columns]
                X        = scaler.transform(df[cols_ok].fillna(df[cols_ok].median()))
                scores   = pca.transform(X)
                if pca.n_components_ == 1:
                    irs_brut = scores[:, 0]
                else:
                    v = pca.explained_variance_ratio_
                    irs_brut = (v[0] / (v[0] + v[1])) * scores[:, 0] + \
                               (v[1] / (v[0] + v[1])) * scores[:, 1]
                irs_min  = seuils.get("irs_min", irs_brut.min())
                irs_max  = seuils.get("irs_max", irs_brut.max())
                df["IRS"] = ((irs_brut - irs_min) / (irs_max - irs_min)).clip(0, 1)
            else:
                raise ValueError("Modèles IRS introuvables")
        except Exception:
            cols = [c for c in ["pm2_5_moyen","dust_moyen","co_moyen","uv_moyen","ozone_moyen"]
                    if c in df.columns]
            irs = sum([
                0.35 * (df["pm2_5_moyen"] / df["pm2_5_moyen"].max()) if "pm2_5_moyen" in df.columns else 0,
                0.25 * (df["dust_moyen"]  / df["dust_moyen"].clip(lower=1).max()) if "dust_moyen" in df.columns else 0,
                0.20 * (df["co_moyen"]    / df["co_moyen"].max()) if "co_moyen" in df.columns else 0,
                0.12 * (df["uv_moyen"]    / df["uv_moyen"].max()) if "uv_moyen" in df.columns else 0,
                0.08 * (df["ozone_moyen"] / df["ozone_moyen"].max()) if "ozone_moyen" in df.columns else 0,
            ])
            df["IRS"] = irs.clip(0, 1) if hasattr(irs, 'clip') else pd.Series([0.1] * len(df))

    # ── Calcul niveau_sanitaire OMS si absent ─────────────────────────────
    if "niveau_sanitaire" not in df.columns:
        SEUIL_AQG = 15; SEUIL_IT4 = 25; SEUIL_IT3 = 37.5
        SEUIL_IT2 = 50; SEUIL_IT1 = 75
        df["niveau_sanitaire"] = df["pm2_5_moyen"].apply(
            lambda x: "🟢 FAIBLE"     if pd.isna(x)       else
                      "🟢 FAIBLE"     if x < SEUIL_AQG    else
                      "🟡 MODÉRÉ"     if x < SEUIL_IT4    else
                      "🟠 ÉLEVÉ"      if x < SEUIL_IT3    else
                      "🔴 TRÈS ÉLEVÉ" if x < SEUIL_IT2    else
                      "🟣 CRITIQUE"   if x < SEUIL_IT1    else
                      "⚫ DANGEREUX"
        )
    
    VILLES = sorted(df["ville"].unique().tolist())
    REGIONS = sorted(df["region"].unique().tolist())

    return df
    


# ══════════════════════════════════════════════════════════════════════════════
# get_context() — RÉACTIVITÉ COMPLÈTE (filtres + lang + theme)
# ══════════════════════════════════════════════════════════════════════════════
def get_context():
    df_brut = load_data()

    villes_sel  = st.session_state.get("ville_sel_list",  "ALL")
    regions_sel = st.session_state.get("region_sel_list", "ALL")
    an_max_data = int(df_brut["date"].dt.year.max())
    an_min_data = int(df_brut["date"].dt.year.min())
    annee_sel   = st.session_state.get("annee_sel", (an_min_data, an_max_data))
    lang        = st.session_state.get("lang",            "fr")
    theme_name  = st.session_state.get("theme_name",      "dark")

    an_min, an_max = int(annee_sel[0]), int(annee_sel[1])

    th = get_theme(theme_name)
    T  = get_t(lang)

    # Seuils OMS AQG 2021 — NCBI NBK574591, Table 3.6
    SEUIL_AQG = 15; SEUIL_IT4 = 25; SEUIL_IT3 = 37.5
    SEUIL_IT2 = 50; SEUIL_IT1 = 75

    # Conserver p50/p75/p90 sur IRS pour compatibilité avec les blocs existants
    p50 = float(df_brut["IRS"].quantile(0.50))
    p75 = float(df_brut["IRS"].quantile(0.75))
    p90 = float(df_brut["IRS"].quantile(0.90))

    df = df_brut.copy()
    df = df[(df["date"].dt.year >= an_min) & (df["date"].dt.year <= an_max)]
    if villes_sel  != "ALL" and isinstance(villes_sel,  list):
        df = df[df["ville"].isin(villes_sel)]
    if regions_sel != "ALL" and isinstance(regions_sel, list):
        df = df[df["region"].isin(regions_sel)]

    if villes_sel == "ALL" or not isinstance(villes_sel, list):
        scope_ville = T["all_cities"]; ville_sel = "(Toutes)"
    elif len(villes_sel) == 1:
        scope_ville = villes_sel[0];   ville_sel = villes_sel[0]
    else:
        scope_ville = f"{len(villes_sel)} villes" if lang == "fr" else f"{len(villes_sel)} cities"
        ville_sel   = "(Toutes)"

    if regions_sel == "ALL" or not isinstance(regions_sel, list):
        scope_region = T["all_regions"]; region_sel = "(Toutes)"
    elif len(regions_sel) == 1:
        scope_region = regions_sel[0]; region_sel = regions_sel[0]
    else:
        scope_region = f"{len(regions_sel)} régions" if lang == "fr" else f"{len(regions_sel)} regions"
        region_sel   = "(Toutes)"

    scope_annees = str(an_min) if an_min == an_max else f"{an_min}–{an_max}"
    scope_label  = f"{scope_ville} · {scope_region} · {scope_annees}"

    if len(df) == 0:
        pm25_moy = irs_moy = 0.0; poll_dom = "—"; n_villes = n_dep_oms = 0
    else:
        pm25_moy  = float(df["pm2_5_moyen"].mean())
        irs_moy   = float(df["IRS"].mean())
        poll_dom  = df["polluant_dominant"].value_counts().index[0] \
                    if "polluant_dominant" in df.columns else "PM2.5"
        n_villes  = int(df["ville"].nunique())
        n_dep_oms = int((df.groupby("ville")["pm2_5_moyen"].mean() > SEUIL_AQG).sum())

    def _f(an):
        d = df_brut[df_brut["date"].dt.year == an]
        if villes_sel  != "ALL" and isinstance(villes_sel,  list): d = d[d["ville"].isin(villes_sel)]
        if regions_sel != "ALL" and isinstance(regions_sel, list): d = d[d["region"].isin(regions_sel)]
        return d

    pm25_fin   = float(_f(an_max)["pm2_5_moyen"].mean())   if len(_f(an_max))   > 0 else pm25_moy
    pm25_prec  = float(_f(an_max - 1)["pm2_5_moyen"].mean()) if len(_f(an_max - 1)) > 0 else pm25_moy
    delta      = pm25_fin - pm25_prec
    tendance   = f"↑ +{delta:.1f}" if delta > 0 else f"↓ {delta:.1f}"
    tend_color = th["red"] if delta > 0 else th["green"]

    if   irs_moy < p50: irs_label, irs_col = T["level_faible"],   th["green"]
    elif irs_moy < p75: irs_label, irs_col = T["level_modere"],   th["amber"]
    elif irs_moy < p90: irs_label, irs_col = T["level_eleve"],    th["coral"]
    else:               irs_label, irs_col = T["level_critique"],  th["red"]

    nk_fr = {
        "FAIBLE":"faible","MODÉRÉ":"modere","ÉLEVÉ":"eleve","CRITIQUE":"critique",
        "LOW":"faible","MODERATE":"modere","HIGH":"eleve","CRITICAL":"critique"
    }
    irs_nk = nk_fr.get(irs_label, "faible")

    return dict(
        df_brut=df_brut, df=df, p50=p50, p75=p75, p90=p90,
        seuil_aqg=SEUIL_AQG, seuil_it4=SEUIL_IT4, seuil_it3=SEUIL_IT3,
        seuil_it2=SEUIL_IT2, seuil_it1=SEUIL_IT1,
        ville_sel=ville_sel, region_sel=region_sel,
        an_min=an_min, an_max=an_max,
        scope_ville=scope_ville, scope_region=scope_region,
        scope_annees=scope_annees, scope_label=scope_label,
        pm25_moy=pm25_moy, irs_moy=irs_moy, poll_dom=poll_dom,
        n_villes=n_villes, n_dep_oms=n_dep_oms,
        tendance=tendance, tend_color=tend_color, delta=delta,
        irs_label=irs_label, irs_color=irs_col, irs_nk=irs_nk,
        lang=lang, th=th, T=T,
        mois=(MOIS_EN if lang == "en" else MOIS_FR),
        coords={
            row["ville"]: (row["latitude"], row["longitude"])
            for _, row in df_brut.drop_duplicates("ville")[["ville","latitude","longitude"]].iterrows()
        }
    )


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS visuels
# ══════════════════════════════════════════════════════════════════════════════
def _rgb(hex_color):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

# ── Icônes SVG inline Premium ───────────────────────────────────────────────
ICONS_SVG = {
    "pm25": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "irs": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m16 12-4-4-4 4"/><path d="M12 8v8"/></svg>',
    "cities": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M3 7v1a3 3 0 0 0 6 0V7m0 1a3 3 0 0 0 6 0V7m0 1a3 3 0 0 0 6 0V7H3Z"/><path d="M5 21V10.85"/><path d="M19 21V10.85"/><path d="M9 21v-4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v4"/></svg>',
    "pollutant": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v10"/><path d="M18 9l-6 6-6-6"/><path d="M22 19H2"/></svg>',
    "trend": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "obs": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    "wind": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/></svg>',
    "temp": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>',
    "rain": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z"/><path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97"/></svg>',
    "fire": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
    "dust": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/></svg>',
}


def banner(img_url, height, title, subtitle, th, accent=None, tint_hex=None, tint_strength=0.32, no_frame=False):
    ac = accent or th["teal"]; tint = tint_hex or ac; r, g, b = _rgb(tint)
    border_style = "none" if no_frame else f"1px solid rgba(249,115,22,0.3)"
    shadow_style = "none" if no_frame else f"0 8px 32px rgba(0,0,0,0.2)"
    
    # Hauteur fixe 120px pour l'unification visuelle
    h = 120 
    
    # Nettoyage et préparation des données
    clean_sub = subtitle.replace('👤','').replace('🩺','').replace('🏛️','').replace('🔬','').strip()
    icon_svg  = _get_profile_svg(subtitle, '#f0f9ff')
    icon_html = f'<div style="margin-right:10px;display:flex;align-items:center;height:24px;">{icon_svg}</div>' if icon_svg else ''

    # Construction du HTML sur une seule ligne pour éviter les bugs de rendu Streamlit
    html_banner = (
        f'<div style="position:relative;width:100%;height:{h}px;border-radius:12px;overflow:hidden;margin-bottom:24px;border:{border_style};box-shadow:{shadow_style};">'
        f'<img src="{img_url}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;filter:brightness(0.3);" onerror="this.style.opacity=\'0\'"/>'
        f'<div style="position:absolute;inset:0;background:linear-gradient(125deg,rgba({r},{g},{b},{tint_strength}) 0%,transparent 100%);"></div>'
        f'<div style="position:absolute;inset:0;padding:20px 30px;display:flex;flex-direction:column;justify-content:flex-end;">'
        f'<div style="font-size:clamp(22px,5vw,42px);font-weight:950;color:#f0f9ff;line-height:1.1;text-transform:uppercase;letter-spacing:1px;text-shadow:0 4px 12px rgba(0,0,0,0.5);">{title}</div>'
        f'<div style="display:flex;align-items:center;margin-top:6px;">{icon_html}'
        f'<div style="font-size:clamp(14px,3vw,20px);color:rgba(255,255,255,0.9);font-weight:950;text-transform:uppercase;letter-spacing:0.8px;line-height:24px;">{clean_sub}</div>'
        f'</div></div></div>'
    )
    st.markdown(html_banner, unsafe_allow_html=True)

def _get_profile_svg(label, color):
    # Mapping simple pour injecter des SVG pro
    lbl = label.upper()
    if "CITOYEN" in lbl or "CITIZEN" in lbl:
        return f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
    if "PROFESSIONNEL" in lbl or "HEALTH" in lbl or "DOCTOR" in lbl:
        return f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m19 10-5.05-1.01a1 1 0 0 1-.81-.68L12 4l-1.14 4.31a1 1 0 0 1-.81.68L5 10l4.31 1.14c.45.12.76.5.76.97V20h4v-7.89c0-.47.31-.85.76-.97L19 10Z"/><path d="M7 20h10"/></svg>'
    if "MAIRE" in lbl or "MAYOR" in lbl or "DÉCIDEUR" in lbl:
        return f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M3 7v1a3 3 0 0 0 6 0V7m0 1a3 3 0 0 0 6 0V7m0 1a3 3 0 0 0 6 0V7H3Z"/><path d="M5 21V10.85"/><path d="M19 21V10.85"/><path d="M9 21v-4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v4"/></svg>'
    if "CHERCHEUR" in lbl or "RESEARCHER" in lbl:
        return f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.31"/><path d="M14 2v7.31"/><path d="M14 9a2 2 0 0 1 2 2v10H8V11a2 2 0 0 1 2-2h4Z"/><path d="M20 20a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2h16v2Z"/></svg>'
    return ""


def img_card(img_url, height, label, desc, th, accent=None, tint_hex=None, tint_strength=0.28, no_frame=False):
    ac = accent or th["teal"]; tint = tint_hex or ac; r, g, b = _rgb(tint)
    border_style = "none" if no_frame else f"1px solid rgba({r},{g},{b},0.26)"
    shadow_style = "none" if no_frame else f"0 2px 18px rgba({r},{g},{b},0.10)"
    st.markdown(f"""
    <div style="position:relative;border-radius:12px;overflow:hidden;height:{height}px;
                border:{border_style};
                box-shadow:{shadow_style};">
        <img src="{img_url}"
             style="width:100%;height:100%;object-fit:cover;
                    filter:saturate(0.85) brightness(0.70);"
             onerror="this.style.opacity='0'"/>
        <div style="position:absolute;inset:0;
                    background:linear-gradient(to top,
                        rgba(2,12,24,0.92) 0%,
                        rgba({r},{g},{b},{tint_strength}) 55%,
                        transparent 100%);"></div>
        <div style="position:absolute;bottom:0;left:0;right:0;padding:14px 16px;">
            <div style="font-size:10px;color:{ac};font-family:'DM Mono',monospace;
                        letter-spacing:.10em;text-transform:uppercase;margin-bottom:3px;">{label}</div>
            <div style="font-size:13px;color:#e0f2fe;font-weight:500;">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def season_card(img_url, periode, titre, detail, accent, th, tint_hex=None):
    tint = tint_hex or accent; r, g, b = _rgb(tint)
    st.markdown(f"""
    <div style="border-radius:12px;overflow:hidden;
                border:1px solid rgba({r},{g},{b},0.24);
                box-shadow:0 2px 14px rgba({r},{g},{b},0.09);">
        <div style="position:relative;height:115px;">
            <img src="{img_url}"
                 style="width:100%;height:100%;object-fit:cover;
                        filter:saturate(0.85) brightness(0.68);"
                 onerror="this.style.opacity='0'"/>
            <div style="position:absolute;inset:0;
                        background:linear-gradient(to bottom,
                            rgba({r},{g},{b},0.28) 0%,
                            rgba(2,12,24,0.84) 100%);"></div>
            <div style="position:absolute;bottom:8px;left:12px;
                        font-size:10px;color:{accent};font-family:'DM Mono',monospace;
                        letter-spacing:.08em;">{periode}</div>
        </div>
        <div style="padding:12px 14px;background:{th['bg_tertiary']};">
            <div style="font-size:13px;font-weight:500;color:{th['text']};margin-bottom:5px;">{titre}</div>
            <div style="font-size:11px;color:{th['text3']};line-height:1.55;">{detail}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_box(value, label, sublabel, color, th, icon=None, animate=True, info_text=None):
    """
    Rendu Premium d'un KPI avec animation de comptage (Count-up) et effets de lueur.
    Support optionnel d'une icône SVG et d'une infobulle (tooltip) discrète.
    """
    r, g, b = _rgb(color)
    is_numeric = False
    target_val = 0
    prefix = ""
    suffix = ""

    # Extraction de la valeur numérique pour l'animation
    try:
        clean_val = str(value).replace(',', '').replace(' ', '')
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", clean_val)
        if nums:
            target_val = float(nums[0])
            is_numeric = True
            parts = re.split(r"[-+]?\d*\.\d+|\d+", str(value), 1)
            prefix = parts[0] if len(parts) > 0 else ""
            suffix = parts[1] if len(parts) > 1 else ""
    except Exception:
        is_numeric = False

    icon_html = ""
    if icon and icon in ICONS_SVG:
        icon_html = f'<div class="icon-box" style="color: {color}; opacity: 0.9; margin-bottom: 8px;">{ICONS_SVG[icon]}</div>'

    info_html = ""
    tooltip_html = ""
    if info_text:
        info_icon_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
        info_html = f"""
        <div class="info-icon" tabindex="0">
            {info_icon_svg}
        </div>
        """
        tooltip_html = f'<div class="tooltip">{info_text}</div>'

    # Design CSS Premium
    html_code = f"""
    <div id="container" style="font-family: 'Inter', sans-serif; text-align: center; overflow: visible; padding: 10px 1px;">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=DM+Mono&display=swap');
            
            .kpi-container {{
                background: {th['bg_card']};
                border: 1px solid rgba({r},{g},{b}, 0.45);
                border-radius: 12px;
                padding: 6px 4px;
                height: 130px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                position: relative;
                cursor: default;
            }}
            
            .kpi-container:hover {{
                transform: translateY(-4px);
                border-color: rgba({r},{g},{b}, 0.8) !important;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3), 0 0 15px rgba({r},{g},{b}, 0.2) !important;
            }}
            
            .value {{
                font-size: 24px;
                font-weight: 800;
                color: {color};
                margin-bottom: 5px;
                line-height: 1.1;
                text-shadow: 0 0 12px rgba({r},{g},{b},0.35);
                letter-spacing: -0.5px;
            }}
            
            .label {{
                font-size: 10.5px;
                font-weight: 700;
                color: {th['text']};
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 3px;
            }}
            
            .sublabel {{
                font-size: 10px;
                color: {th['text2']};
                opacity: 1;
                font-weight: 600;
            }}
            
            .icon-box svg {{
                width: 20px;
                height: 20px;
            }}

            .info-icon {{
                position: absolute;
                top: 8px;
                right: 8px;
                width: 16px;
                height: 16px;
                color: {th['text3']};
                cursor: pointer;
                transition: color 0.2s;
                z-index: 10;
            }}
            
            .info-icon:hover {{
                color: {color};
            }}

            .tooltip {{
                visibility: hidden;
                opacity: 0;
                position: absolute;
                top: 135px; /* Placed exactly below the container */
                left: 50%; /* Centered horizontally */
                width: 96%; /* Responsive width to avoid clipping */
                box-sizing: border-box;
                background-color: {th['bg_elevated']};
                color: {th['text']};
                text-align: center;
                padding: 6px 8px;
                border-radius: 8px;
                border: 1px solid rgba({r},{g},{b}, 0.4);
                box-shadow: 0 6px 16px rgba(0,0,0,0.4);
                font-size: 9.5px;
                font-weight: 600;
                line-height: 1.35;
                z-index: 9999;
                transition: opacity 0.3s ease, transform 0.3s ease, visibility 0s linear 0.3s;
                transform: translate(-50%, 5px);
                pointer-events: none;
                word-wrap: break-word;
                white-space: normal;
            }}

            .info-icon:hover ~ .tooltip,
            .info-icon:focus ~ .tooltip {{
                visibility: visible;
                opacity: 1;
                transform: translate(-50%, 0);
                transition: opacity 0.3s ease, transform 0.3s ease, visibility 0s;
            }}
        </style>

        <div class="kpi-container">
            {info_html}
            {tooltip_html}
            {icon_html}
            <div class="value">
                {prefix}<span id="count-up">0</span>{suffix}
            </div>
            <div class="label">{label}</div>
            <div class="sublabel">{sublabel}</div>
        </div>

        <script>
            function animateValue(obj, start, end, duration) {{
                let startTimestamp = null;
                const step = (timestamp) => {{
                    if (!startTimestamp) startTimestamp = timestamp;
                    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                    const val = progress * (end - start) + start;
                    
                    if (end % 1 === 0) {{
                        obj.innerHTML = Math.floor(val).toLocaleString();
                    }} else {{
                        obj.innerHTML = val.toFixed(end.toString().split('.')[1]?.length || 1);
                    }}
                    
                    if (progress < 1) {{
                        window.requestAnimationFrame(step);
                    }}
                }};
                window.requestAnimationFrame(step);
            }}

            const el = document.getElementById("count-up");
            const target = {target_val if is_numeric else 0};
            
            if ({'true' if animate and is_numeric else 'false'}) {{
                setTimeout(() => {{
                    animateValue(el, 0, target, 1500);
                }}, 200);
            }} else {{
                el.innerHTML = "{value}".replace("{prefix}", "").replace("{suffix}", "");
            }}
        </script>
    </div>
    """
    st_html(html_code, height=250)

def sources_bar(text, th):
    st.markdown(f"""
    <div style="font-size:10px;color:{th['text3']};font-family:'DM Mono',monospace;
                letter-spacing:.02em;border-top:1px solid {th['border_soft']};
                padding-top:10px;margin-top:14px;">{text}</div>
    """, unsafe_allow_html=True)


def empty_state(T, th):
    st.markdown(f"""
    <div style="background:rgba(245,158,11,0.10);
                border:1px solid rgba(245,158,11,0.25);
                border-radius:12px;padding:28px;text-align:center;margin:20px 0;">
        <div style="font-size:24px;margin-bottom:8px;">⚠️</div>
        <div style="font-size:14px;color:{th['amber']};font-weight:500;">{T['no_data']}</div>
    </div>
    """, unsafe_allow_html=True)


def irs_level(val, p50, p75, p90, T, th):
    if val < p50: return th["green"], T["level_faible"],   "faible"
    if val < p75: return th["amber"], T["level_modere"],   "modere"
    if val < p90: return th["coral"], T["level_eleve"],    "eleve"
    return              th["red"],   T["level_critique"],  "critique"


def irs_color(val, p50, p75, p90):
    th = get_theme(st.session_state.get("theme_name", "dark"))
    T  = get_t(st.session_state.get("lang", "fr"))
    c, l, nk = irs_level(val, p50, p75, p90, T, th)
    emoji = {"faible": "🟢", "modere": "🟡", "eleve": "🟠", "critique": "🔴"}[nk]
    return c, f"{emoji} {l}", nk

# ══════════════════════════════════════════════════════════════════════════════
# Charger les seuils contextuels
# ══════════════════════════════════════════════════════════════════════════════

# Charger les seuils contextuels


def _load_seuils_contextuels():
    import os, joblib
    chemins = [
        'models/seuils_contextuels.pkl',
        '../models/seuils_contextuels.pkl',
    ]
    for c in chemins:
        if os.path.exists(c):
            return joblib.load(c)
    return None

SEUILS_CONTEXTUELS = _load_seuils_contextuels()

def niveau_contextuel(pm25, ville):
    """
    Retourne le niveau contextuel camerounais basé sur p90 historique.
    Référence : Percentile 90 · AirSentinel 2022-2026 · INS Cameroun (2019)
    """
    if SEUILS_CONTEXTUELS is None:
        return None, None

    seuil_p90 = SEUILS_CONTEXTUELS['par_ville'].get(ville, None)
    if seuil_p90 is None:
        return None, None

    ratio = pm25 / seuil_p90

    if   ratio >= 1.0:  return "PIC ANORMAL",  "red"    # dépasse p90 local
    elif ratio >= 0.75: return "ÉLEVÉ",         "coral"  # 75-100% du p90
    elif ratio >= 0.50: return "MODÉRÉ",        "amber"  # 50-75% du p90
    else:               return "NORMAL",        "green"  # < 50% du p90