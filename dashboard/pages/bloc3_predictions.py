# ============================================================
# Bloc 3 — Prédictions visuelles
# Responsable : FANKAM Marc Aurel
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np

def afficher(profil="Citoyen"):
    st.title("🔮 Prédictions — PM2.5 & Risque sanitaire")

    try:
        df      = pd.read_excel('data/processed/dataset_final.xlsx')
        df['date'] = pd.to_datetime(df['date'])
        modele  = joblib.load('models/meilleur_modele.pkl')
        features = joblib.load('models/features.pkl')
        seuils  = joblib.load('models/seuils_irs.pkl')
    except Exception as e:
        st.error(f"❌ Fichiers manquants : {e}")
        st.info("Lance d'abord les notebooks 01 à 05.")
        return

    # ── Simulateur ───────────────────────────────────────────
    st.subheader("🎛️ Simulateur — Prédire PM2.5")
    st.caption("Ajuste les conditions météo pour voir la prédiction")

    col1, col2 = st.columns(2)
    with col1:
        ville = st.selectbox("🏙️ Ville", sorted(df['ville'].unique()))
        temp  = st.slider("🌡️ Température max (°C)", 15, 45, 30)
        vent  = st.slider("💨 Vent max (km/h)", 0, 80, 15)
        pluie = st.slider("🌧️ Précipitations (mm)", 0, 50, 0)
    with col2:
        mois     = st.selectbox("📅 Mois", range(1, 13),
                                format_func=lambda x: ['Jan','Fév','Mar','Avr','Mai','Jun',
                                                        'Jul','Aoû','Sep','Oct','Nov','Déc'][x-1])
        sunshine = st.slider("☀️ Ensoleillement (h)", 0, 12, 8)
        humidite = st.slider("💧 Humidité (%)", 10, 100, 60)

    # Préparer les données pour la prédiction
    row_meteo = {f: 0 for f in features}
    mappings = {
        'temperature_2m_max': temp,
        'temperature_2m_mean': temp - 5,
        'temperature_2m_min': temp - 10,
        'wind_speed_10m_max': vent,
        'precipitation_sum': pluie,
        'sunshine_duration': sunshine * 3600,
        'mois': mois,
        'relative_humidity_2m_mean': humidite,
    }
    for k, v in mappings.items():
        if k in row_meteo:
            row_meteo[k] = v

    # Coordonnées de la ville
    ville_data = df[df['ville'] == ville].iloc[0] if len(df[df['ville'] == ville]) > 0 else None
    if ville_data is not None:
        if 'latitude' in features:  row_meteo['latitude']  = ville_data['latitude']
        if 'longitude' in features: row_meteo['longitude'] = ville_data['longitude']

    X_pred = pd.DataFrame([row_meteo])[features].fillna(0)

    try:
        pm25_predit = float(modele.predict(X_pred)[0])
        pm25_predit = max(0, pm25_predit)
    except:
        pm25_predit = df[df['ville'] == ville]['pm2_5_moyen'].mean()

    # Niveau d'alerte
    if pm25_predit < 15:   niveau, couleur = "🟢 BON",      "green"
    elif pm25_predit < 25: niveau, couleur = "🟡 MODÉRÉ",   "orange"
    elif pm25_predit < 35: niveau, couleur = "🟠 MAUVAIS",  "darkorange"
    else:                   niveau, couleur = "🔴 DANGEREUX","red"

    # Afficher le résultat
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("💨 PM2.5 prédit", f"{pm25_predit:.1f} µg/m³",
                f"Seuil OMS : 15 µg/m³", delta_color="inverse")
    col2.metric("📊 Niveau", niveau)
    col3.metric("🏙️ Ville", ville)

    st.divider()

    # ── Historique de la ville ────────────────────────────────
    st.subheader(f"📈 Historique PM2.5 — {ville}")
    df_ville = df[df['ville'] == ville].groupby('date')['pm2_5_moyen'].mean().reset_index()

    fig = px.line(df_ville, x='date', y='pm2_5_moyen',
                  title=f'PM2.5 à {ville} — 2022-2025',
                  labels={'pm2_5_moyen': 'PM2.5 (µg/m³)', 'date': 'Date'})
    fig.add_hline(y=15, line_color='red', line_dash='dash',
                  annotation_text='Seuil OMS')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    # ── Calendrier de risque ──────────────────────────────────
    st.subheader(f"📅 Calendrier de risque mensuel — {ville}")
    df_ville_mois = df[df['ville'] == ville].copy()
    df_ville_mois['mois_nom'] = df_ville_mois['date'].dt.strftime('%b %Y')
    cal = df_ville_mois.groupby(df_ville_mois['date'].dt.to_period('M'))['pm2_5_moyen'].mean()
    cal.index = cal.index.astype(str)

    fig3 = px.bar(x=cal.index, y=cal.values,
                  color=cal.values,
                  color_continuous_scale=['green', 'orange', 'red'],
                  labels={'x': 'Mois', 'y': 'PM2.5 (µg/m³)'})
    fig3.add_hline(y=15, line_color='red', line_dash='dash')
    fig3.update_layout(height=300)
    st.plotly_chart(fig3, use_container_width=True)
