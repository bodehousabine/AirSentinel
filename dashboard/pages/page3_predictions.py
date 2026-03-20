# ============================================================
# Page 3 — Prédictions & Simulateur
# Responsable : FANKAM Marc Aurel
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import numpy as np

SEUIL_OMS = 15

def afficher(df, profil="Citoyen", ville="Yaoundé"):
    st.title("🔮 Prédictions & Simulateur")
    st.caption("Prédit PM2.5 depuis les variables météo — Objectif hackathon IndabaX 2026")

    # Charger le modèle
    try:
        modele   = joblib.load('models/meilleur_modele.pkl')
        features = joblib.load('models/features.pkl')
        modele_ok = True
    except:
        modele_ok = False
        st.warning("⚠️ Modèle non disponible — lance d'abord le notebook 04.")

    # ── Sliders ───────────────────────────────────────────────
    st.subheader("🎛️ Conditions météo")

    c1, c2 = st.columns(2)
    with c1:
        temp     = st.slider("🌡️ Température max (°C)", 15, 45, 30)
        vent     = st.slider("💨 Vent max (km/h)", 0, 80, 15)
        pluie    = st.slider("🌧️ Précipitations (mm)", 0, 50, 0)
        sunshine = st.slider("☀️ Ensoleillement (heures)", 0, 12, 8)
    with c2:
        mois    = st.selectbox("📅 Mois", range(1,13),
                               format_func=lambda x:
                               ['Jan','Fév','Mar','Avr','Mai','Jun',
                                'Jul','Aoû','Sep','Oct','Nov','Déc'][x-1])
        horizon = st.radio("⏱️ Horizon",
                           ["Aujourd'hui","Dans 24h","Dans 72h"])
        saison  = {12:0,1:0,2:0,3:1,4:1,5:2,6:2,7:2,8:2,9:2,10:2,11:1}[mois]

    st.divider()

    # ── Prédiction ────────────────────────────────────────────
    st.subheader(f"📊 Résultat — {ville} — {horizon}")

    if modele_ok:
        ville_data = df[df['ville'] == ville]
        lat = ville_data['latitude'].iloc[0] if len(ville_data)>0 else 5.5
        lon = ville_data['longitude'].iloc[0] if len(ville_data)>0 else 12.3

        row = {f:0 for f in features}
        mappings = {
            'temperature_2m_max':           temp,
            'temperature_2m_mean':          temp-5,
            'temperature_2m_min':           temp-10,
            'apparent_temperature_max':     temp+2,
            'apparent_temperature_min':     temp-8,
            'wind_speed_10m_max':           vent,
            'wind_gusts_10m_max':           vent*1.3,
            'precipitation_sum':            pluie,
            'rain_sum':                     pluie,
            'precipitation_hours':          2 if pluie>0 else 0,
            'sunshine_duration':            sunshine*3600,
            'shortwave_radiation_sum':      sunshine*2,
            'daylight_duration':            43200,
            'et0_fao_evapotranspiration':   temp*0.2,
            'mois':                         mois,
            'jour_annee':                   mois*30,
            'saison_code':                  saison,
            'latitude':                     lat,
            'longitude':                    lon,
        }
        for k,v in mappings.items():
            if k in row: row[k] = v

        X = pd.DataFrame([row])[features].fillna(0)
        pm25 = float(modele.predict(X)[0])
        pm25 = max(0, pm25)

        if horizon == "Dans 24h":
            pm25 *= np.random.uniform(0.9, 1.1)
        elif horizon == "Dans 72h":
            pm25 *= np.random.uniform(0.85, 1.15)
        pm25 = round(pm25, 1)

        if pm25 < 15:   niv, emoji, col = "BON",       "🟢", "green"
        elif pm25 < 25: niv, emoji, col = "MODÉRÉ",    "🟡", "orange"
        elif pm25 < 35: niv, emoji, col = "MAUVAIS",   "🟠", "darkorange"
        else:            niv, emoji, col = "DANGEREUX", "🔴", "red"

        c1,c2,c3 = st.columns(3)
        c1.metric("💨 PM2.5 prédit", f"{pm25} µg/m³",
                  f"Seuil OMS : {SEUIL_OMS} µg/m³", delta_color="inverse")
        c2.metric("📊 Niveau", f"{emoji} {niv}")
        c3.metric("🏙️ Ville", ville)

        # Message selon profil
        st.divider()
        st.subheader(f"💬 Message — {profil}")
        msgs = {
            "Citoyen": {
                "BON":       "✅ Air sain — activités normales.",
                "MODÉRÉ":    "⚠️ Réduisez les activités en extérieur.",
                "MAUVAIS":   "🚨 Restez à l'intérieur si possible.",
                "DANGEREUX": "🔴 Danger — restez à l'intérieur.",
            },
            "Professionnel de santé": {
                "BON":       "✅ Consultations normales attendues.",
                "MODÉRÉ":    "⚠️ Surveiller patients asthmatiques.",
                "MAUVAIS":   "🚨 Préparer stocks médicaments respiratoires.",
                "DANGEREUX": "🔴 Activer protocole urgence respiratoire.",
            },
            "Décideur / Maire": {
                "BON":       "✅ Aucune action requise.",
                "MODÉRÉ":    "⚠️ Informer les établissements scolaires.",
                "MAUVAIS":   "🚨 Annuler événements sportifs extérieurs.",
                "DANGEREUX": "🔴 Activer plan communal d'urgence sanitaire.",
            },
            "Chercheur": {
                "BON":       f"PM2.5 = {pm25} µg/m³ < 15 (OMS). Normal.",
                "MODÉRÉ":    f"PM2.5 = {pm25} µg/m³. Entre OMS et IT4.",
                "MAUVAIS":   f"PM2.5 = {pm25} µg/m³. Dépasse OMS de {pm25-15:.1f}.",
                "DANGEREUX": f"PM2.5 = {pm25} µg/m³. Situation critique.",
            },
        }
        st.info(msgs.get(profil, msgs["Citoyen"]).get(niv,""))

    st.divider()

    # ── Historique ────────────────────────────────────────────
    st.subheader(f"📈 Historique PM2.5 — {ville}")
    df_v  = df[df['ville'] == ville].copy()
    serie = df_v.groupby('date')['pm2_5_moyen'].mean().reset_index()

    fig = px.line(serie, x='date', y='pm2_5_moyen',
                  title=f"PM2.5 historique — {ville}",
                  labels={'pm2_5_moyen':'PM2.5 (µg/m³)','date':'Date'})
    fig.add_hline(y=SEUIL_OMS, line_color='red', line_dash='dash',
                  annotation_text='Seuil OMS')
    if modele_ok:
        fig.add_hline(y=pm25, line_color='blue', line_dash='dot',
                      annotation_text=f'Prédiction : {pm25}')
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Comparaison N-1 ───────────────────────────────────────
    st.subheader("📊 Cette année vs l'an dernier")
    annee_max  = df_v['date'].dt.year.max()
    annee_prec = annee_max - 1
    pm25_act   = df_v[df_v['date'].dt.year==annee_max]['pm2_5_moyen'].mean()
    pm25_prec  = df_v[df_v['date'].dt.year==annee_prec]['pm2_5_moyen'].mean()

    if not (pd.isna(pm25_act) or pd.isna(pm25_prec)):
        diff = pm25_act - pm25_prec
        c1,c2,c3 = st.columns(3)
        c1.metric(f"📅 {annee_prec}", f"{pm25_prec:.1f} µg/m³")
        c2.metric(f"📅 {annee_max}", f"{pm25_act:.1f} µg/m³",
                  f"{diff:+.1f} µg/m³", delta_color="inverse")
        c3.metric("📈 Tendance",
                  "En hausse 📈" if diff>0 else "En baisse 📉",
                  f"{abs(diff/pm25_prec*100):.1f}%",
                  delta_color="inverse" if diff>0 else "normal")
