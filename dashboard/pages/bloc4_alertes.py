# ============================================================
# Bloc 4 — Système d'alertes automatiques
# Responsable : FANKAM Marc Aurel
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import joblib

def afficher(profil="Citoyen"):
    st.title("🚨 Alertes — Niveaux de risque sanitaire")
    st.caption("Basé sur l'IRS par ACP et les seuils percentiles 50/75/90")

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

    # ── Sélecteur ville ───────────────────────────────────────
    ville = st.selectbox("🏙️ Choisir une ville", sorted(df['ville'].unique()))
    df_v  = df[df['ville'] == ville].copy()
    irs_actuel = df_v['IRS'].iloc[-1] if len(df_v) > 0 else 0

    # ── Niveau d'alerte actuel ────────────────────────────────
    if irs_actuel < p50:
        niveau, couleur, emoji = "FAIBLE",   "#22c55e", "🟢"
    elif irs_actuel < p75:
        niveau, couleur, emoji = "MODÉRÉ",   "#eab308", "🟡"
    elif irs_actuel < p90:
        niveau, couleur, emoji = "ÉLEVÉ",    "#f97316", "🟠"
    else:
        niveau, couleur, emoji = "CRITIQUE", "#ef4444", "🔴"

    st.markdown(f"""
    <div style='background-color:{couleur}22; border-left:5px solid {couleur};
                padding:20px; border-radius:8px; margin:10px 0'>
        <h2 style='color:{couleur}'>{emoji} Niveau {niveau} — {ville}</h2>
        <p>IRS = {irs_actuel:.3f} | Seuils : p50={p50:.3f} | p75={p75:.3f} | p90={p90:.3f}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Messages selon profil ─────────────────────────────────
    st.subheader(f"💬 Message pour : {profil}")

    messages = {
        "Citoyen": {
            "FAIBLE":   "✅ Air sain — vous pouvez sortir normalement.",
            "MODÉRÉ":   "⚠️ Réduisez les activités intenses en extérieur.",
            "ÉLEVÉ":    "🚨 Restez à l'intérieur si possible, surtout les enfants.",
            "CRITIQUE": "🔴 Danger — restez à l'intérieur, fermez les fenêtres."
        },
        "Professionnel de santé": {
            "FAIBLE":   "✅ Flux normal de consultations attendu.",
            "MODÉRÉ":   "⚠️ Surveiller les patients asthmatiques.",
            "ÉLEVÉ":    "🚨 Préparer stocks médicaments respiratoires.",
            "CRITIQUE": "🔴 ACTIVER PROTOCOLE URGENCE — Commander bronchodilatateurs."
        },
        "Décideur / Maire": {
            "FAIBLE":   "✅ Aucune action requise.",
            "MODÉRÉ":   "⚠️ Informer les établissements scolaires.",
            "ÉLEVÉ":    "🚨 Annuler événements sportifs. Envoyer SMS d'alerte.",
            "CRITIQUE": "🔴 Activer plan communal sanitaire d'urgence."
        },
        "Chercheur": {
            "FAIBLE":   f"IRS={irs_actuel:.3f} < p50={p50:.3f} — Situation normale.",
            "MODÉRÉ":   f"IRS={irs_actuel:.3f} entre p50={p50:.3f} et p75={p75:.3f}.",
            "ÉLEVÉ":    f"IRS={irs_actuel:.3f} entre p75={p75:.3f} et p90={p90:.3f}.",
            "CRITIQUE": f"IRS={irs_actuel:.3f} ≥ p90={p90:.3f} — Pire que 90% des jours."
        }
    }

    msg = messages.get(profil, messages["Citoyen"]).get(niveau, "")
    st.info(msg)

    st.divider()

    # ── Tableau de référence ──────────────────────────────────
    st.subheader("📋 Tableau des niveaux d'alerte")
    data_tableau = {
        "Niveau": ["🟢 FAIBLE", "🟡 MODÉRÉ", "🟠 ÉLEVÉ", "🔴 CRITIQUE"],
        "Seuil IRS": [f"< {p50:.3f}", f"{p50:.3f} – {p75:.3f}",
                      f"{p75:.3f} – {p90:.3f}", f"≥ {p90:.3f}"],
        "Signification": [
            "Journée normale au Cameroun",
            "Pire que 50% des jours observés",
            "Pire que 75% des jours observés",
            "Pire que 90% des jours observés"
        ]
    }
    st.dataframe(pd.DataFrame(data_tableau), use_container_width=True, hide_index=True)

    st.divider()

    # ── Historique IRS de la ville ────────────────────────────
    st.subheader(f"📈 Historique IRS — {ville}")
    fig = px.line(df_v, x='date', y='IRS',
                  title=f'Évolution IRS — {ville}',
                  labels={'IRS': 'IRS', 'date': 'Date'})
    fig.add_hline(y=p90, line_color='red',    line_dash='dash', annotation_text='CRITIQUE')
    fig.add_hline(y=p75, line_color='orange', line_dash='dash', annotation_text='ÉLEVÉ')
    fig.add_hline(y=p50, line_color='green',  line_dash='dash', annotation_text='MODÉRÉ')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
