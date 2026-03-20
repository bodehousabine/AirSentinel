# ============================================================
# Bloc 1 — Carte interactive du Cameroun
# Responsable : BODEHOU Sabine
# ============================================================

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

def afficher(profil="Citoyen"):
    st.title("🗺️ Carte nationale — Qualité de l'air")
    st.caption("Source : Open-Meteo · Seuil OMS PM2.5 = 15 µg/m³ (WHO AQG 2021, NCBI NBK574591)")

    # Charger les données
    try:
        df = pd.read_excel('data/processed/dataset_final.xlsx')
        df['date'] = pd.to_datetime(df['date'])
    except:
        st.error("❌ Fichier data/processed/dataset_final.xlsx introuvable.")
        st.info("Lance d'abord les notebooks 01 à 05.")
        return

    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        annee = st.selectbox("📅 Année", sorted(df['date'].dt.year.unique(), reverse=True))
    with col2:
        saison = st.selectbox("🌤️ Saison", ["Toute l'année", "Saison sèche", "Saison des pluies"])
    with col3:
        variable = st.selectbox("🔬 Variable", ["PM2.5", "IRS", "Dust"])

    # Filtrer
    df_f = df[df['date'].dt.year == annee].copy()
    if saison == "Saison sèche":
        df_f = df_f[df_f['saison_code'] == 0]
    elif saison == "Saison des pluies":
        df_f = df_f[df_f['saison_code'] == 2]

    # Calculer moyennes par ville
    col_var = {'PM2.5': 'pm2_5_moyen', 'IRS': 'IRS', 'Dust': 'dust_moyen'}[variable]
    if col_var not in df_f.columns:
        st.warning(f"Variable {variable} non disponible.")
        return

    df_villes = df_f.groupby('ville').agg(
        valeur=(col_var, 'mean'),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first'),
        region=('region', 'first')
    ).reset_index().dropna()

    # Créer la carte
    m = folium.Map(location=[5.5, 12.3], zoom_start=6, tiles='CartoDB positron')

    for _, row in df_villes.iterrows():
        if variable == 'PM2.5':
            if row['valeur'] < 15:   couleur = 'green'
            elif row['valeur'] < 35: couleur = 'orange'
            else:                     couleur = 'red'
        elif variable == 'IRS':
            p90 = df_f['IRS'].quantile(0.90) if 'IRS' in df_f.columns else 0.7
            if row['valeur'] < df_f['IRS'].quantile(0.50):   couleur = 'green'
            elif row['valeur'] < df_f['IRS'].quantile(0.75): couleur = 'orange'
            else:                                              couleur = 'red'
        else:
            couleur = 'blue'

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=12,
            color=couleur,
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(
                f"<b>{row['ville']}</b><br>"
                f"Région : {row['region']}<br>"
                f"{variable} moyen : {row['valeur']:.1f}<br>"
                f"Seuil OMS PM2.5 : 15 µg/m³",
                max_width=200
            ),
            tooltip=f"{row['ville']} — {variable} = {row['valeur']:.1f}"
        ).add_to(m)

    st_folium(m, width=800, height=500)

    # Légende
    st.markdown("**Légende :** 🟢 Bon (< 15 µg/m³) · 🟠 Modéré (15-35) · 🔴 Dangereux (> 35)")

    # Tableau récapitulatif selon profil
    if profil in ["Décideur / Maire", "Chercheur"]:
        st.subheader("📋 Détail par ville")
        df_villes_sorted = df_villes.sort_values('valeur', ascending=False)
        st.dataframe(df_villes_sorted[['ville', 'region', 'valeur']].rename(
            columns={'valeur': f'{variable} moyen'}
        ), use_container_width=True)
