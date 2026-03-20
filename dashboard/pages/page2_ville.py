# ============================================================
# Page 2 — Ma ville (tout sur une seule page)
# Responsable : FANKAM Marc Aurel + PEURBAR Firmin
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

SEUIL_OMS = 15

def afficher(df, profil="Citoyen", ville="Yaoundé"):

    df_v   = df[df['ville'] == ville].copy()
    region = df_v['region'].iloc[0] if len(df_v) > 0 else ""

    st.title(f"🏙️ {ville} — {region}")
    st.caption(f"Profil : {profil} · Période 2022-2025")

    if len(df_v) == 0:
        st.warning(f"Pas de données pour {ville}")
        return

    # ── SECTION 1 — KPIs ─────────────────────────────────────
    st.subheader("📊 Indicateurs clés")
    pm25_moy = df_v['pm2_5_moyen'].mean()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("💨 PM2.5 moyen", f"{pm25_moy:.1f} µg/m³",
              f"{pm25_moy-SEUIL_OMS:+.1f} vs OMS", delta_color="inverse")
    if 'dust_moyen' in df_v.columns:
        c2.metric("💨 Dust moyen", f"{df_v['dust_moyen'].mean():.1f} µg/m³","Harmattan")
    if 'co_moyen' in df_v.columns:
        c3.metric("🔥 CO moyen", f"{df_v['co_moyen'].mean():.1f} µg/m³","Feux brousse")
    if 'us_aqi_moyen' in df_v.columns:
        c4.metric("📊 AQI moyen", f"{df_v['us_aqi_moyen'].mean():.0f}","Indice qualité")

    st.divider()

    # ── SECTION 2 — Tous les polluants ───────────────────────
    st.subheader("🔬 Tous les polluants")

    polluants = {
        'pm2_5_moyen': ('PM2.5','µg/m³', SEUIL_OMS),
        'pm10_moyen':  ('PM10', 'µg/m³', 45),
        'dust_moyen':  ('Dust', 'µg/m³', None),
        'co_moyen':    ('CO',   'µg/m³', 4000),
        'no2_moyen':   ('NO2',  'µg/m³', 25),
        'so2_moyen':   ('SO2',  'µg/m³', 40),
        'ozone_moyen': ('Ozone','µg/m³', 100),
    }
    poll_dispo = {k:v for k,v in polluants.items() if k in df_v.columns}

    if poll_dispo:
        noms    = [v[0] for v in poll_dispo.values()]
        valeurs = [df_v[k].mean() for k in poll_dispo.keys()]
        seuils  = [v[2] for v in poll_dispo.values()]

        couleurs = ['#ef4444' if s and val>s else '#22c55e'
                    for val,s in zip(valeurs,seuils)]

        fig = go.Figure(go.Bar(x=noms, y=valeurs, marker_color=couleurs))
        fig.update_layout(height=280,
                         title="Concentration moyenne par polluant",
                         showlegend=False,
                         yaxis_title="µg/m³")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🔴 Rouge = dépasse seuil OMS · 🟢 Vert = sous seuil OMS (WHO AQG 2021)")

    st.divider()

    # ── SECTION 3 — Évolution temporelle ─────────────────────
    st.subheader("📈 Évolution dans le temps")

    variable = st.selectbox(
        "Variable à afficher",
        list(poll_dispo.keys()),
        format_func=lambda x: poll_dispo[x][0]
    )

    serie = df_v.groupby('date')[variable].mean().reset_index()
    fig2  = px.line(serie, x='date', y=variable,
                    title=f"{poll_dispo[variable][0]} — {ville} 2022-2025",
                    labels={variable: f"{poll_dispo[variable][0]} ({poll_dispo[variable][1]})",
                            'date':'Date'})
    if poll_dispo[variable][2]:
        fig2.add_hline(y=poll_dispo[variable][2], line_color='red',
                       line_dash='dash',
                       annotation_text=f"Seuil OMS = {poll_dispo[variable][2]}")
    fig2.update_layout(height=280)
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── SECTION 4 — Calendrier de risque mensuel ──────────────
    st.subheader("📅 Calendrier de risque mensuel")
    st.caption("Niveau de pollution chaque mois — rouge = dangereux, vert = sain")

    mois_labels = {1:'Jan',2:'Fév',3:'Mar',4:'Avr',5:'Mai',6:'Jun',
                   7:'Jul',8:'Aoû',9:'Sep',10:'Oct',11:'Nov',12:'Déc'}

    df_v['mois'] = df_v['date'].dt.month
    cal = df_v.groupby('mois')['pm2_5_moyen'].mean().reset_index()
    cal['mois_nom'] = cal['mois'].map(mois_labels)
    cal['niveau']   = cal['pm2_5_moyen'].apply(
        lambda x: '🔴 DANGEREUX' if x>35
             else '🟠 MAUVAIS'   if x>25
             else '🟡 MODÉRÉ'    if x>SEUIL_OMS
             else '🟢 BON'
    )

    fig3 = px.bar(cal, x='mois_nom', y='pm2_5_moyen',
                  color='pm2_5_moyen',
                  color_continuous_scale=['green','yellow','orange','red'],
                  text='niveau',
                  title=f"Calendrier de risque — {ville}",
                  labels={'mois_nom':'Mois','pm2_5_moyen':'PM2.5 (µg/m³)'})
    fig3.add_hline(y=SEUIL_OMS, line_color='red', line_dash='dash',
                   annotation_text='Seuil OMS 15 µg/m³')
    fig3.update_traces(textposition='outside', textfont_size=10)
    fig3.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── SECTION 5 — Saisonnalité ──────────────────────────────
    st.subheader("🌤️ Saisonnalité — Pire mois")

    mois_max = cal.loc[cal['pm2_5_moyen'].idxmax(), 'mois_nom']
    mois_min = cal.loc[cal['pm2_5_moyen'].idxmin(), 'mois_nom']

    c1,c2,c3 = st.columns(3)
    c1.metric("🔴 Mois le + pollué", mois_max,
              f"{cal['pm2_5_moyen'].max():.1f} µg/m³")
    c2.metric("🟢 Mois le + sain",   mois_min,
              f"{cal['pm2_5_moyen'].min():.1f} µg/m³")
    c3.metric("📊 Amplitude",
              f"{cal['pm2_5_moyen'].max()-cal['pm2_5_moyen'].min():.1f} µg/m³",
              "Variation annuelle")

    st.divider()

    # ── SECTION 6 — Épisodes climatiques ─────────────────────
    st.subheader("⚡ Épisodes climatiques — " + ville)
    st.caption("Percentile 90 — Ceccherini et al. 2017")

    c1,c2,c3,c4 = st.columns(4)
    episodes = {
        'vague_chaleur':        ('🌡️','Vagues chaleur',   c1),
        'harmattan_intense':    ('💨','Harmattan',         c2),
        'episode_feux':         ('🔥','Feux brousse',      c3),
        'humidite_infectieuse': ('💧','Humidité infect.',  c4),
    }
    for col_ep,(emoji,nom,col) in episodes.items():
        if col_ep in df_v.columns:
            nb  = df_v[col_ep].sum()
            pct = df_v[col_ep].mean()*100
            col.metric(f"{emoji} {nom}", f"{nb:,} j", f"{pct:.1f}%")

    st.divider()

    # ── SECTION 7 — Comparaison N-1 ──────────────────────────
    st.subheader("📊 Comparaison avec l'année précédente")

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
