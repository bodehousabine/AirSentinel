# ============================================================
# Bloc 5 — Aide à la décision médicale
# Responsable : PEURBAR RIMBAR Firmin
# ============================================================

import streamlit as st
import pandas as pd
import joblib

def afficher(profil="Citoyen"):
    st.title("🏥 Aide à la décision médicale")
    st.caption("Recommandations basées sur les percentiles IRS — pas sur des chiffres inventés")

    try:
        df     = pd.read_excel('data/processed/dataset_final.xlsx')
        df['date'] = pd.to_datetime(df['date'])
        seuils = joblib.load('models/seuils_irs.pkl')
        p50    = seuils['p50']
        p75    = seuils['p75']
        p90    = seuils['p90']
    except Exception as e:
        st.error(f"❌ Fichiers manquants : {e}")
        return

    if 'IRS' not in df.columns:
        st.warning("IRS non calculé — lance d'abord le notebook 05.")
        return

    # ── Sélecteur ─────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        ville = st.selectbox("🏙️ Ville", sorted(df['ville'].unique()))
    with col2:
        date_sel = st.date_input("📅 Date")

    df_v = df[df['ville'] == ville]
    irs  = df_v['IRS'].mean() if len(df_v) > 0 else 0.3

    # ── Niveau ───────────────────────────────────────────────
    if irs < p50:   niveau = "FAIBLE"
    elif irs < p75: niveau = "MODÉRÉ"
    elif irs < p90: niveau = "ÉLEVÉ"
    else:           niveau = "CRITIQUE"

    st.divider()

    # ── Recommandations selon profil ──────────────────────────
    if profil == "Professionnel de santé":
        st.subheader("👨‍⚕️ Recommandations médicales")

        reco = {
            "FAIBLE": {
                "statut":        "🟢 Situation normale",
                "medicaments":   "Stock habituel suffisant",
                "personnel":     "Effectif normal",
                "consultations": "Flux normal attendu",
                "lits":          "Aucun lit supplémentaire nécessaire"
            },
            "MODÉRÉ": {
                "statut":        "🟡 Vigilance modérée",
                "medicaments":   "Surveiller stocks bronchodilatateurs",
                "personnel":     "Alerter 1-2 médecins supplémentaires",
                "consultations": "Légère augmentation possible 24-72h",
                "lits":          "Prévoir 2-3 lits respiratoires"
            },
            "ÉLEVÉ": {
                "statut":        "🟠 Risque élevé",
                "medicaments":   "Préparer stocks médicaments respiratoires",
                "personnel":     "Appeler personnel de renfort",
                "consultations": f"Augmentation attendue — pire que 75% des jours",
                "lits":          "Préparer 5-10 lits supplémentaires"
            },
            "CRITIQUE": {
                "statut":        "🔴 ALERTE CRITIQUE",
                "medicaments":   "COMMANDER EN URGENCE : bronchodilatateurs, corticoïdes",
                "personnel":     "Activer protocole urgence — tout le personnel",
                "consultations": f"Situation exceptionnelle — pire que 90% des jours",
                "lits":          "Activer plan d'urgence hospitalier"
            }
        }[niveau]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Statut", reco["statut"])
            st.info(f"💊 **Médicaments** : {reco['medicaments']}")
            st.info(f"👥 **Personnel** : {reco['personnel']}")
        with col2:
            st.info(f"🩺 **Consultations** : {reco['consultations']}")
            st.info(f"🛏️ **Lits** : {reco['lits']}")

    elif profil == "Décideur / Maire":
        st.subheader("🏛️ Actions recommandées")
        actions = []
        if irs >= p50: actions.append("📢 Informer les établissements scolaires")
        if irs >= p75: actions.append("🏃 Annuler les événements sportifs extérieurs")
        if irs >= p75: actions.append("📱 Envoyer SMS d'alerte préventive aux habitants")
        if irs >= p90: actions.append("🚨 Activer le plan communal de gestion sanitaire")
        if irs >= p90: actions.append("📞 Contacter le Ministère de la Santé")

        if not actions:
            st.success("✅ Aucune action requise — situation normale")
        else:
            for action in actions:
                st.warning(action)

    else:  # Citoyen ou Chercheur
        st.subheader("👤 Conseils personnalisés")
        conseils = {
            "FAIBLE":   "✅ Air sain — sortez normalement.",
            "MODÉRÉ":   "⚠️ Réduisez les activités intenses en extérieur.",
            "ÉLEVÉ":    "🚨 Restez à l'intérieur si possible.",
            "CRITIQUE": "🔴 Restez à l'intérieur, fermez les fenêtres."
        }
        st.info(conseils[niveau])

    st.divider()

    # ── Populations vulnérables ───────────────────────────────
    st.subheader("👥 Populations vulnérables")
    st.caption("Seuils OMS 2021 — NCBI NBK574591, Table 3.6")

    pm25_actuel = df_v['pm2_5_moyen'].mean() if len(df_v) > 0 else 0
    populations = [
        ("👶 Enfants (< 15 ans)",      pm25_actuel > 15, "Évitez les activités en extérieur"),
        ("🤰 Femmes enceintes",         pm25_actuel > 15, "Restez à l'intérieur si possible"),
        ("👴 Personnes âgées (> 60)",   pm25_actuel > 25, "Prenez vos médicaments respiratoires"),
        ("🫁 Asthmatiques",             pm25_actuel > 15, "Gardez votre bronchodilatateur à portée"),
        ("🌾 Agriculteurs",             irs > p75,        "Portez un masque pour les travaux"),
    ]

    for nom, alerte, message in populations:
        if alerte:
            st.error(f"{nom} → ⚠️ {message}")
        else:
            st.success(f"{nom} → ✅ Pas d'alerte particulière")
