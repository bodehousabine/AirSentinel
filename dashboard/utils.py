"""
utils.py — AirSentinel Cameroun
get_context() avec lang + theme, composants visuels adaptatifs.
OPTIMISÉ : lecture parquet (5-10x plus rapide que xlsx)
"""
global VILLES, REGIONS
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib, os, base64
from themes import get_theme, THEMES
from translations import get_t

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
    an_max_data = df_brut["date"].dt.year.max()
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


def banner(img_url, height, title, subtitle, th, accent=None, tint_hex=None, tint_strength=0.32, no_frame=False):
    ac = accent or th["teal"]; tint = tint_hex or ac; r, g, b = _rgb(tint)
    border_style = "none" if no_frame else f"1px solid rgba(249,115,22,0.3)"
    shadow_style = "none" if no_frame else f"0 8px 32px rgba(0,0,0,0.2)"
    
    # Hauteur fixe 120px pour l'unification visuelle
    h = 120 
    
    st.markdown(f"""
    <div style="position:relative;width:100%;height:{h}px;border-radius:12px;
                overflow:hidden;margin-bottom:24px;
                border:{border_style};
                box-shadow:{shadow_style};">
        <img src="{img_url}"
             style="position:absolute;inset:0;width:100%;height:100%;
                    object-fit:cover;object-position:center;
                    filter:brightness(0.3);"
             onerror="this.style.opacity='0'"/>
        <div style="position:absolute;inset:0;
                    background:linear-gradient(125deg,
                        rgba({r},{g},{b},{tint_strength}) 0%,
                        transparent 100%);"></div>
        <div style="position:absolute;inset:0;padding:20px 30px;
                    display:flex;flex-direction:column;justify-content:flex-end;">
            <div style="font-size:clamp(22px, 5vw, 42px);font-weight:950;color:#f0f9ff;line-height:1.1;
                        text-transform:uppercase;letter-spacing:1px;
                        text-shadow:0 4px 12px rgba(0,0,0,0.5);"> {title}</div>
            <div style="font-size:clamp(14px, 3vw, 20px);color:rgba(255,255,255,0.9);
                        font-weight:950;text-transform:uppercase;margin-top:4px;
                        letter-spacing:0.8px;">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


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


def kpi_box(value, label, sublabel, color, th):
    r, g, b = _rgb(color)
    st.markdown(f"""
    <div style="background:linear-gradient(165deg,{th['bg_tertiary']} 0%,{th['bg_elevated']} 100%);
                border:1px solid rgba({r},{g},{b},0.3);border-top:3px solid {color};
                border-radius:14px;padding:20px 12px;text-align:center;height:120px;
                display:flex;flex-direction:column;justify-content:center;
                box-shadow:0 4px 20px rgba(0,0,0,0.2), 0 0 15px rgba({r},{g},{b},0.12);
                transition: transform 0.2s ease-in-out;">
        <div style="font-size:clamp(22px, 4vw, 28px);font-weight:800;color:{color};
                    margin-bottom:6px;line-height:1.2;
                    text-shadow: 0 0 12px rgba({r},{g},{b},0.4);
                    font-family:'Inter', sans-serif;">{value}</div>
        <div style="font-size:12px;font-weight:600;color:{th['text']};
                    text-transform:uppercase;letter-spacing:0.05em;">{label}</div>
        <div style="font-size:10px;color:{th['text3']};margin-top:5px;
                    opacity:0.8;">{sublabel}</div>
    </div>
    """, unsafe_allow_html=True)


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