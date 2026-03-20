# ============================================================
# Bloc 2 — Indicateurs clés (KPIs)
# Responsable : BODEHOU Sabine
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

def afficher(profil="Citoyen"):
    st.title("📊 Indicateurs clés — AirSentinel Cameroun")
    st.caption("Seuil OMS PM2.5 = 15 µg/m³ — WHO AQG 2021 (NCBI NBK574591, Table 3.6)")

    try:
        df = pd.read_excel('data/processed/dataset_final.xlsx')
        df['date'] = pd.to_datetime(df['date'])
    except:
        st.error("❌ Fichier data/processed/dataset_final.xlsx introuvable.")
        return

    SEUIL_OMS = 15

    # ── KPIs principaux ──────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    pm25_moy = df['pm2_5_moyen'].mean()
    with col1:
        delta = f"+{pm25_moy - SEUIL_OMS:.1f} vs OMS" if pm25_moy > SEUIL_OMS else f"{pm25_moy - SEUIL_OMS:.1f} vs OMS"
        st.metric("💨 PM2.5 moyen national", f"{pm25_moy:.1f} µg/m³", delta,
                  delta_color="inverse")

    if 'IRS' in df.columns:
        irs_moy = df['IRS'].mean()
        with col2:
            st.metric("🏥 IRS national moyen", f"{irs_moy:.3f}", "Calculé par ACP")

    villes_depasse = df[df['pm2_5_moyen'] > SEUIL_OMS]['ville'].nunique()
    total_villes   = df['ville'].nunique()
    with col3:
        st.metric("🏙️ Villes dépassant OMS",
                  f"{villes_depasse}/{total_villes}",
                  f"{villes_depasse/total_villes*100:.0f}% des villes")

    jours_critiques = (df['pm2_5_moyen'] > SEUIL_OMS).mean() * 100
    with col4:
        st.metric("📅 Jours dépassant OMS", f"{jours_critiques:.1f}%",
                  delta_color="inverse")

    st.divider()

    # ── Graphique évolution PM2.5 ─────────────────────────────
    st.subheader("📈 Évolution PM2.5 national")
    serie = df.groupby('date')['pm2_5_moyen'].mean().reset_index()
    fig = px.line(serie, x='date', y='pm2_5_moyen',
                  title='PM2.5 moyen national — 2022-2025',
                  labels={'pm2_5_moyen': 'PM2.5 (µg/m³)', 'date': 'Date'})
    fig.add_hline(y=SEUIL_OMS, line_color='red', line_dash='dash',
                  annotation_text='Seuil OMS 15 µg/m³')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── PM2.5 par région ─────────────────────────────────────
    st.subheader("🗺️ PM2.5 moyen par région")
    df_region = df.groupby('region')['pm2_5_moyen'].mean().reset_index().sort_values('pm2_5_moyen', ascending=True)
    fig2 = px.bar(df_region, x='pm2_5_moyen', y='region', orientation='h',
                  color='pm2_5_moyen',
                  color_continuous_scale=['green', 'orange', 'red'],
                  labels={'pm2_5_moyen': 'PM2.5 (µg/m³)', 'region': 'Région'})
    fig2.add_vline(x=SEUIL_OMS, line_color='red', line_dash='dash',
                   annotation_text='OMS')
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Épisodes actifs (pour décideurs) ─────────────────────
    if profil in ["Décideur / Maire", "Professionnel de santé"]:
        st.divider()
        st.subheader("⚠️ Épisodes climatiques actifs")
        col1, col2, col3, col4 = st.columns(4)
        episodes = {
            'vague_chaleur': ('🌡️', 'Vagues de chaleur'),
            'harmattan_intense': ('💨', 'Harmattan intense'),
            'episode_feux': ('🔥', 'Feux de brousse'),
            'humidite_infectieuse': ('💧', 'Humidité infectieuse')
        }
        for i, (col_ep, (emoji, nom)) in enumerate(episodes.items()):
            if col_ep in df.columns:
                nb_jours = df[col_ep].sum()
                [col1, col2, col3, col4][i].metric(f"{emoji} {nom}", f"{nb_jours:,} jours")
