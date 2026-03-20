# ============================================================
# AirSentinel Cameroun — Dashboard Principal v3
# Équipe DPA Green Tech — IndabaX 2026
# 4 pages : Nationale / Ma ville / Prédictions / Santé
# ============================================================

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AirSentinel Cameroun",
    page_icon="🌍",
    layout="wide"
)

from pages import page1_nationale
from pages import page2_ville
from pages import page3_predictions
from pages import page4_sante

@st.cache_data
def charger_donnees():
    try:
        df = pd.read_excel('data/processed/dataset_final.xlsx')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return None

df = charger_donnees()

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.image("https://flagcdn.com/w80/cm.png", width=60)
st.sidebar.title("🌍 AirSentinel")
st.sidebar.caption("IndabaX Cameroon 2026 — DPA Green Tech")
st.sidebar.divider()

profil = st.sidebar.selectbox("👤 Je suis...", [
    "Citoyen",
    "Professionnel de santé",
    "Décideur / Maire",
    "Chercheur"
])

if df is not None:
    villes = sorted(df['ville'].unique())
else:
    villes = ["Yaoundé", "Douala", "Maroua", "Garoua"]

ville = st.sidebar.selectbox("🏙️ Ma ville", villes)

st.sidebar.divider()

page = st.sidebar.radio("📍 Navigation", [
    "🌍 Vue nationale",
    "🏙️ Ma ville",
    "🔮 Prédictions",
    "🏥 Santé & Recommandations"
])

st.sidebar.divider()
st.sidebar.caption("ISSEA + ENSP Yaoundé · 2026")

# ── Affichage ─────────────────────────────────────────────────
if df is None:
    st.error("❌ Dataset introuvable. Lance d'abord les notebooks 01 à 05.")
    st.stop()

if page == "🌍 Vue nationale":
    page1_nationale.afficher(df, profil)
elif page == "🏙️ Ma ville":
    page2_ville.afficher(df, profil, ville)
elif page == "🔮 Prédictions":
    page3_predictions.afficher(df, profil, ville)
elif page == "🏥 Santé & Recommandations":
    page4_sante.afficher(df, profil, ville)
