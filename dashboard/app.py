# ============================================================
# AirSentinel Cameroun — Dashboard Principal
# Équipe DPA Green Tech — IndabaX 2026
# ============================================================

import streamlit as st

st.set_page_config(
    page_title="AirSentinel Cameroun",
    page_icon="🌍",
    layout="wide"
)

# Import des blocs
from pages import bloc1_carte
from pages import bloc2_kpis
from pages import bloc3_predictions
from pages import bloc4_alertes
from pages import bloc5_aide_medicale
from pages import bloc6_contexte

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.image("https://flagcdn.com/w80/cm.png", width=80)
st.sidebar.title("🌍 AirSentinel")
st.sidebar.caption("Hackathon IndabaX Cameroon 2026")
st.sidebar.divider()

# Sélecteur de profil
profil = st.sidebar.selectbox("👤 Je suis...", [
    "Citoyen",
    "Professionnel de santé",
    "Décideur / Maire",
    "Chercheur"
])

st.sidebar.divider()

# Navigation
page = st.sidebar.radio("📍 Navigation", [
    "🗺️ Carte nationale",
    "📊 Indicateurs clés",
    "🔮 Prédictions",
    "🚨 Alertes",
    "🏥 Aide médicale",
    "ℹ️ Contexte"
])

st.sidebar.divider()
st.sidebar.caption("DPA Green Tech — ISSEA + ENSP Yaoundé")

# ── Affichage du bloc sélectionné ────────────────────────────
if page == "🗺️ Carte nationale":
    bloc1_carte.afficher(profil)
elif page == "📊 Indicateurs clés":
    bloc2_kpis.afficher(profil)
elif page == "🔮 Prédictions":
    bloc3_predictions.afficher(profil)
elif page == "🚨 Alertes":
    bloc4_alertes.afficher(profil)
elif page == "🏥 Aide médicale":
    bloc5_aide_medicale.afficher(profil)
elif page == "ℹ️ Contexte":
    bloc6_contexte.afficher(profil)
