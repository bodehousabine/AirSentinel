# ============================================================
# Page 4 — Santé & Recommandations
# Responsable : PEURBAR RIMBAR Firmin
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import joblib

SEUIL_OMS = 15

def afficher(df, profil="Citoyen", ville="Yaoundé"):
    st.title("🏥 Santé & Recommandations")
    st.caption("Basé sur l'IRS (ACP) et les seuils OMS 2021 — NCBI NBK574591")

    # Charger seuils IRS
    try:
        seuils = joblib.load('models/seuils_irs.pkl')
        p50, p75, p90 = seuils['p50'], seuils['p75'], seuils['p90']
    except:
        p50, p75, p90 = 0.3, 0.6, 0.8

    df_v     = df[df['ville'] == ville].copy()
    pm25_val = df_v['pm2_5_moyen'].mean() if len(df_v)>0 else 0
    irs_val  = df_v['IRS'].mean() if 'IRS' in df_v.columns and len(df_v)>0 else 0.3

    # Niveau IRS
    if irs_val < p50:   niv, bg, fg = "FAIBLE",   "#f0fdf4","#166534"
    elif irs_val < p75: niv, bg, fg = "MODÉRÉ",   "#fefce8","#854d0e"
    elif irs_val < p90: niv, bg, fg = "ÉLEVÉ",    "#fff7ed","#9a3412"
    else:                niv, bg, fg = "CRITIQUE", "#fef2f2","#991b1b"

    # ── SECTION 1 — Niveau IRS ────────────────────────────────
    st.subheader("📊 Niveau de risque sanitaire")

    st.markdown(f"""
    <div style='background:{bg};border-left:5px solid {fg};
                padding:16px;border-radius:8px;margin-bottom:16px;'>
        <div style='font-size:20px;font-weight:500;color:{fg};'>
            Niveau {niv} — {ville}
        </div>
        <div style='font-size:13px;color:{fg};margin-top:6px;'>
            IRS = {irs_val:.3f} · PM2.5 = {pm25_val:.1f} µg/m³ · Seuil OMS = {SEUIL_OMS} µg/m³
        </div>
        <div style='font-size:12px;color:{fg};margin-top:4px;'>
            Seuils : p50={p50:.3f} · p75={p75:.3f} · p90={p90:.3f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tableau des 4 niveaux
    data_niv = {
        "Niveau":        ["🟢 FAIBLE","🟡 MODÉRÉ","🟠 ÉLEVÉ","🔴 CRITIQUE"],
        "Seuil IRS":     [f"< {p50:.3f}",
                          f"{p50:.3f} – {p75:.3f}",
                          f"{p75:.3f} – {p90:.3f}",
                          f"≥ {p90:.3f}"],
        "Signification": [
            "Journée normale au Cameroun",
            "Pire que 50% des jours observés",
            "Pire que 75% des jours observés",
            "Pire que 90% des jours observés"
        ]
    }
    st.dataframe(pd.DataFrame(data_niv), use_container_width=True, hide_index=True)

    st.divider()

    # ── SECTION 2 — Recommandations selon profil ──────────────
    st.subheader(f"💬 Recommandations — {profil}")

    if profil == "Professionnel de santé":
        reco = {
            "FAIBLE":   ("Stock habituel suffisant",
                         "Effectif normal",
                         "Flux normal attendu",
                         "Aucun lit supplémentaire"),
            "MODÉRÉ":   ("Surveiller stocks bronchodilatateurs",
                         "Alerter 1-2 médecins supplémentaires",
                         "Légère augmentation possible 24-72h",
                         "Prévoir 2-3 lits respiratoires"),
            "ÉLEVÉ":    ("Préparer stocks médicaments respiratoires",
                         "Appeler personnel de renfort",
                         "Augmentation attendue — pire que 75% des jours",
                         "Préparer 5-10 lits supplémentaires"),
            "CRITIQUE": ("COMMANDER EN URGENCE : bronchodilatateurs",
                         "Activer protocole urgence complet",
                         "Situation exceptionnelle — pire que 90% des jours",
                         "Activer plan d'urgence hospitalier"),
        }[niv]

        c1,c2 = st.columns(2)
        with c1:
            st.info(f"💊 **Médicaments**\n\n{reco[0]}")
            st.info(f"👥 **Personnel**\n\n{reco[1]}")
        with c2:
            st.info(f"🩺 **Consultations**\n\n{reco[2]}")
            st.info(f"🛏️ **Lits**\n\n{reco[3]}")

    elif profil == "Décideur / Maire":
        st.subheader("🏛️ Actions prioritaires")
        actions = []
        if irs_val >= p50: actions.append("📢 Informer les établissements scolaires")
        if irs_val >= p75: actions.append("🏃 Annuler les événements sportifs extérieurs")
        if irs_val >= p75: actions.append("📱 Envoyer SMS d'alerte aux habitants")
        if irs_val >= p90: actions.append("🚨 Activer le plan communal sanitaire")
        if irs_val >= p90: actions.append("📞 Contacter le Ministère de la Santé")

        if not actions:
            st.success("✅ Aucune action requise — situation normale")
        else:
            for a in actions:
                st.warning(a)

    else:
        msgs = {
            "FAIBLE":   "✅ Air sain — vous pouvez sortir normalement.",
            "MODÉRÉ":   "⚠️ Réduisez les activités intenses en extérieur.",
            "ÉLEVÉ":    "🚨 Restez à l'intérieur si possible, surtout les enfants.",
            "CRITIQUE": "🔴 Danger — restez à l'intérieur, fermez les fenêtres.",
        }
        st.info(msgs[niv])

    st.divider()

    # ── SECTION 3 — Populations vulnérables ──────────────────
    st.subheader("👥 Populations vulnérables")
    st.caption("Seuils OMS 2021 — NCBI NBK574591, Table 3.6")

    populations = [
        ("👶","Enfants (< 15 ans)",     pm25_val>15,  "Évitez les activités en extérieur",   "PM2.5 > 15 µg/m³ (OMS)"),
        ("🤰","Femmes enceintes",        pm25_val>15,  "Restez à l'intérieur si possible",    "PM2.5 > 15 µg/m³ (OMS)"),
        ("👴","Personnes âgées (> 60)", pm25_val>25,  "Prenez vos médicaments respiratoires","PM2.5 > 25 µg/m³ (OMS IT4)"),
        ("🫁","Asthmatiques",            pm25_val>15,  "Gardez votre bronchodilatateur",       "PM2.5 > 15 µg/m³ (OMS)"),
        ("🌾","Agriculteurs",            irs_val>p75,  "Portez un masque aux champs",          "IRS > percentile 75"),
        ("👨","Tout le monde",           pm25_val>35,  "Restez à l'intérieur, fermez fenêtres","PM2.5 > 35 µg/m³ (OMS IT3)"),
    ]

    for emoji,nom,alerte,message,source in populations:
        if alerte:
            st.error(f"{emoji} **{nom}** — ⚠️ {message} *(Source : {source})*")
        else:
            st.success(f"{emoji} **{nom}** — ✅ Pas d'alerte particulière")

    st.divider()

    # ── SECTION 4 — Historique IRS ────────────────────────────
    if 'IRS' in df_v.columns:
        st.subheader(f"📈 Historique IRS — {ville}")
        serie_irs = df_v.groupby('date')['IRS'].mean().reset_index()

        fig = px.line(serie_irs, x='date', y='IRS',
                      title=f"Évolution IRS — {ville}",
                      labels={'IRS':'IRS','date':'Date'})
        fig.add_hline(y=p90, line_color='red',    line_dash='dash',
                      annotation_text=f'CRITIQUE (p90={p90:.3f})')
        fig.add_hline(y=p75, line_color='orange', line_dash='dash',
                      annotation_text=f'ÉLEVÉ (p75={p75:.3f})')
        fig.add_hline(y=p50, line_color='green',  line_dash='dash',
                      annotation_text=f'MODÉRÉ (p50={p50:.3f})')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
