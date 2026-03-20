# ============================================================
# Bloc 6 — Informations contextuelles
# Responsable : PEURBAR RIMBAR Firmin
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

def afficher(profil="Citoyen"):
    st.title("ℹ️ Contexte — Comprendre la pollution")

    try:
        df = pd.read_excel('data/processed/dataset_final.xlsx')
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        st.error(f"❌ Fichiers manquants : {e}")
        return

    ville = st.selectbox("🏙️ Ville", sorted(df['ville'].unique()))
    df_v  = df[df['ville'] == ville].copy()

    st.divider()

    # ── Cause principale ─────────────────────────────────────
    st.subheader("🔍 Cause principale de la pollution")

    if 'polluant_dominant' in df_v.columns:
        cause = df_v['polluant_dominant'].mode()[0] if len(df_v) > 0 else "Inconnue"
        causes_freq = df_v['polluant_dominant'].value_counts()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🏆 Polluant dominant", cause)
            st.caption("Calculé sur toute la période disponible")
        with col2:
            fig = px.pie(values=causes_freq.values,
                         names=causes_freq.index,
                         title="Répartition des polluants dominants")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Variable polluant_dominant non disponible.")

    st.divider()

    # ── Contexte saisonnier ───────────────────────────────────
    st.subheader("📅 Contexte saisonnier")

    mois_labels = {1:'Jan',2:'Fév',3:'Mar',4:'Avr',5:'Mai',6:'Jun',
                   7:'Jul',8:'Aoû',9:'Sep',10:'Oct',11:'Nov',12:'Déc'}
    saison_labels = {0:'🏜️ Saison sèche', 1:'🌤️ Transition', 2:'🌧️ Saison des pluies'}

    df_v['mois']     = df_v['date'].dt.month
    df_v['mois_nom'] = df_v['mois'].map(mois_labels)
    df_v['saison']   = df_v['saison_code'].map(saison_labels) if 'saison_code' in df_v.columns else 'N/A'

    mois_pm25 = df_v.groupby('mois_nom')['pm2_5_moyen'].mean().reset_index()
    mois_order = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
    mois_pm25['mois_nom'] = pd.Categorical(mois_pm25['mois_nom'], categories=mois_order, ordered=True)
    mois_pm25 = mois_pm25.sort_values('mois_nom')

    fig2 = px.bar(mois_pm25, x='mois_nom', y='pm2_5_moyen',
                  color='pm2_5_moyen',
                  color_continuous_scale=['green', 'orange', 'red'],
                  title=f'PM2.5 moyen par mois — {ville}',
                  labels={'mois_nom': 'Mois', 'pm2_5_moyen': 'PM2.5 (µg/m³)'})
    fig2.add_hline(y=15, line_color='red', line_dash='dash',
                   annotation_text='Seuil OMS')
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Comparaison N-1 ───────────────────────────────────────
    st.subheader("📊 Comparaison avec l'année précédente")

    annee_max = df_v['date'].dt.year.max()
    annee_prec = annee_max - 1

    pm25_actuel = df_v[df_v['date'].dt.year == annee_max]['pm2_5_moyen'].mean()
    pm25_prec   = df_v[df_v['date'].dt.year == annee_prec]['pm2_5_moyen'].mean()

    if not pd.isna(pm25_actuel) and not pd.isna(pm25_prec):
        diff = pm25_actuel - pm25_prec
        col1, col2, col3 = st.columns(3)
        col1.metric(f"📅 {annee_prec}", f"{pm25_prec:.1f} µg/m³")
        col2.metric(f"📅 {annee_max}", f"{pm25_actuel:.1f} µg/m³",
                    f"{diff:+.1f} µg/m³", delta_color="inverse")
        col3.metric("📈 Tendance",
                    "📈 En hausse" if diff > 0 else "📉 En baisse",
                    f"{abs(diff/pm25_prec*100):.1f}%")

    st.divider()

    # ── Épisodes climatiques ──────────────────────────────────
    st.subheader("⚡ Épisodes climatiques détectés")
    st.caption("Méthode : percentile 90 par région — Ceccherini et al. 2017")

    episodes = {
        'vague_chaleur':       ('🌡️', 'Vagues de chaleur',     'Ceccherini et al. 2017'),
        'harmattan_intense':   ('💨', 'Harmattan intense',      'Bauer et al. 2024'),
        'episode_feux':        ('🔥', 'Feux de brousse',        'Barker et al. 2020'),
        'humidite_infectieuse':('💧', 'Humidité infectieuse',   'DHS Afrique subsaharienne'),
    }

    for col_ep, (emoji, nom, ref) in episodes.items():
        if col_ep in df_v.columns:
            nb = df_v[col_ep].sum()
            pct = df_v[col_ep].mean() * 100
            st.write(f"{emoji} **{nom}** : {nb:,} jours ({pct:.1f}%) — *Réf : {ref}*")

    st.divider()

    # ── À propos du projet ────────────────────────────────────
    with st.expander("ℹ️ À propos d'AirSentinel Cameroun"):
        st.markdown("""
        **Équipe DPA Green Tech — IndabaX Cameroon 2026**

        - BODEHOU Sabine (ISSEA) — Statisticienne
        - FANKAM Marc Aurel (ISSEA) — Modélisation
        - PEURBAR RIMBAR Firmin (ISSEA) — SHAP & Rapport
        - FOFACK ALEMDJOU Henri Joël (ENSP) — Dashboard & API

        **Références scientifiques :**
        - WHO AQG 2021 — https://www.ncbi.nlm.nih.gov/books/NBK574591/
        - Ceccherini et al. 2017 — https://doi.org/10.1038/s41598-017-03107-6
        - Barker et al. 2020 — https://acp.copernicus.org/articles/20/15443/2020/
        - Bauer et al. 2024 — https://pmc.ncbi.nlm.nih.gov/articles/PMC11523266/
        """)
