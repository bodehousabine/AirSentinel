# ============================================================
# Page 1 — Vue nationale
# Responsable : BODEHOU Sabine
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

SEUIL_OMS = 15  # WHO AQG 2021 — NCBI NBK574591, Table 3.6

def afficher(df, profil="Citoyen"):
    st.title("🌍 Vue nationale — Qualité de l'air au Cameroun")
    st.caption("Seuil OMS PM2.5 = 15 µg/m³ — WHO AQG 2021 (NCBI NBK574591, Table 3.6)")

    # ── Filtres ───────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        annee = st.selectbox("📅 Année",
                             sorted(df['date'].dt.year.unique(), reverse=True))
    with col2:
        saison = st.selectbox("🌤️ Saison",
                              ["Toute l'année","Saison sèche","Saison des pluies"])

    df_f = df[df['date'].dt.year == annee].copy()
    if saison == "Saison sèche":
        df_f = df_f[df_f['saison_code'] == 0]
    elif saison == "Saison des pluies":
        df_f = df_f[df_f['saison_code'] == 2]

    st.divider()

    # ── KPIs ──────────────────────────────────────────────────
    pm25_moy       = df_f['pm2_5_moyen'].mean()
    villes_depasse = df_f[df_f['pm2_5_moyen'] > SEUIL_OMS]['ville'].nunique()
    total_villes   = df_f['ville'].nunique()
    jours_depasse  = (df_f['pm2_5_moyen'] > SEUIL_OMS).mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💨 PM2.5 national", f"{pm25_moy:.1f} µg/m³",
              f"{pm25_moy-SEUIL_OMS:+.1f} vs OMS", delta_color="inverse")
    c2.metric("🏙️ Villes > OMS", f"{villes_depasse}/{total_villes}",
              f"{villes_depasse/total_villes*100:.0f}%")
    c3.metric("📅 Jours > OMS", f"{jours_depasse:.1f}%", delta_color="inverse")
    if 'IRS' in df_f.columns:
        c4.metric("🏥 IRS national", f"{df_f['IRS'].mean():.3f}", "Par ACP")

    st.divider()

    # ── Carte ─────────────────────────────────────────────────
    st.subheader("🗺️ Carte des villes")

    df_villes = df_f.groupby('ville').agg(
        pm25=('pm2_5_moyen','mean'),
        lat=('latitude','first'),
        lon=('longitude','first'),
        region=('region','first')
    ).reset_index().dropna()

    m = folium.Map(location=[5.5,12.3], zoom_start=6, tiles='CartoDB positron')

    for _, row in df_villes.iterrows():
        if row['pm25'] < SEUIL_OMS: couleur = 'green'
        elif row['pm25'] < 35:       couleur = 'orange'
        else:                         couleur = 'red'

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=10, color=couleur, fill=True, fill_opacity=0.8,
            popup=folium.Popup(
                f"<b>{row['ville']}</b><br>Région : {row['region']}<br>"
                f"PM2.5 = {row['pm25']:.1f} µg/m³<br>Seuil OMS = {SEUIL_OMS} µg/m³",
                max_width=200),
            tooltip=f"{row['ville']} — {row['pm25']:.1f} µg/m³"
        ).add_to(m)

    st_folium(m, width=800, height=450)
    st.caption("🟢 < 15 µg/m³ · 🟠 15-35 µg/m³ · 🔴 > 35 µg/m³")

    st.divider()

    # ── PM2.5 par région ──────────────────────────────────────
    st.subheader("📊 PM2.5 par région")
    df_reg = df_f.groupby('region')['pm2_5_moyen'].mean().reset_index()
    df_reg = df_reg.sort_values('pm2_5_moyen', ascending=True)

    fig = px.bar(df_reg, x='pm2_5_moyen', y='region', orientation='h',
                 color='pm2_5_moyen',
                 color_continuous_scale=['green','orange','red'],
                 labels={'pm2_5_moyen':'PM2.5 (µg/m³)','region':'Région'})
    fig.add_vline(x=SEUIL_OMS, line_color='red', line_dash='dash',
                  annotation_text='Seuil OMS')
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Épisodes climatiques ──────────────────────────────────
    st.subheader("⚡ Épisodes climatiques actifs")
    st.caption("Méthode : percentile 90 par région — Ceccherini et al. 2017")

    episodes = {
        'vague_chaleur':        ('🌡️','Vagues de chaleur'),
        'harmattan_intense':    ('💨','Harmattan intense'),
        'episode_feux':         ('🔥','Feux de brousse'),
        'humidite_infectieuse': ('💧','Humidité infectieuse'),
    }
    cols = st.columns(4)
    for i,(col_ep,(emoji,nom)) in enumerate(episodes.items()):
        if col_ep in df_f.columns:
            nb  = df_f[col_ep].sum()
            pct = df_f[col_ep].mean()*100
            cols[i].metric(f"{emoji} {nom}", f"{nb:,} jours", f"{pct:.1f}%")
