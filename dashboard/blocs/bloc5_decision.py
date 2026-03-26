"""blocs/bloc5_decision.py — Décision santé · 2 sous-onglets + populations vulnérables"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils import get_context, img_card, sources_bar, empty_state, irs_level
from assets import IMAGES

_SNK_TO_KEY    = {"faible":"normal","modere":"watch","eleve":"high","critique":"urgent"}
_SNK_TO_STATUS = {"faible":"bloc5_status_normal","modere":"bloc5_status_watch",
                  "eleve":"bloc5_status_high","critique":"bloc5_status_urgent"}
_SNK_TO_MAYOR  = {"faible":"bloc5_status_calm","modere":"bloc5_status_watch",
                  "eleve":"bloc5_status_alert","critique":"bloc5_status_crisis"}

# ── Recommandations populations vulnérables ───────────────────────────────────
VULN_FR = {
    "faible": {
        "enfants":    "✅ Activités extérieures normales autorisées.",
        "enceintes":  "✅ Sorties normales. Aération intérieure recommandée.",
        "ages":       "✅ Activité physique légère possible en extérieur.",
        "asthma":     "✅ Gardez votre bronchodilatateur à portée par précaution.",
        "agricult":   "✅ Travaux agricoles sans restriction particulière.",
    },
    "modere": {
        "enfants":    "⚠️ Réduire les jeux intensifs en plein air. Favoriser les activités intérieures.",
        "enceintes":  "⚠️ Limiter les sorties prolongées. Éviter les axes très fréquentés.",
        "ages":       "⚠️ Éviter les efforts physiques en extérieur. Surveiller la respiration.",
        "asthma":     "⚠️ Avoir le bronchodilatateur accessible. Limiter l'exposition.",
        "agricult":   "⚠️ Porter un masque FFP2 lors des travaux. Faire des pauses fréquentes.",
    },
    "eleve": {
        "enfants":    "🚨 Annuler les cours de sport en extérieur. Garder les enfants à l'intérieur.",
        "enceintes":  "🚨 Rester à l'intérieur. Consulter un médecin si gêne respiratoire.",
        "ages":       "🚨 Rester à l'intérieur. Prendre les médicaments préventifs.",
        "asthma":     "🚨 Utiliser le bronchodilatateur en prévention. Contacter le médecin.",
        "agricult":   "🚨 Interrompre les travaux aux heures chaudes. Masque FFP2 obligatoire.",
    },
    "critique": {
        "enfants":    "🔴 DANGER — Ne pas sortir. Fermer fenêtres. Appeler le médecin si symptômes.",
        "enceintes":  "🔴 DANGER — Confinement strict. Consultation médicale urgente recommandée.",
        "ages":       "🔴 DANGER — Rester confiné. Activer le suivi médical d'urgence.",
        "asthma":     "🔴 DANGER CRITIQUE — Traitement d'urgence. Appeler le 15 si crise.",
        "agricult":   "🔴 DANGER — Cesser tout travail extérieur. Ne sortir qu'en cas d'absolue nécessité.",
    },
}
VULN_EN = {
    "faible": {
        "enfants":    "✅ Normal outdoor activities allowed.",
        "enceintes":  "✅ Normal outings. Indoor ventilation recommended.",
        "ages":       "✅ Light physical activity possible outdoors.",
        "asthma":     "✅ Keep bronchodilator handy as precaution.",
        "agricult":   "✅ Agricultural work without particular restriction.",
    },
    "modere": {
        "enfants":    "⚠️ Reduce intense outdoor play. Prefer indoor activities.",
        "enceintes":  "⚠️ Limit prolonged outings. Avoid busy roads.",
        "ages":       "⚠️ Avoid physical exertion outdoors. Monitor breathing.",
        "asthma":     "⚠️ Keep bronchodilator accessible. Limit exposure.",
        "agricult":   "⚠️ Wear FFP2 mask during work. Take frequent breaks.",
    },
    "eleve": {
        "enfants":    "🚨 Cancel outdoor sports. Keep children indoors.",
        "enceintes":  "🚨 Stay indoors. See doctor if breathing difficulty.",
        "ages":       "🚨 Stay indoors. Take preventive medications.",
        "asthma":     "🚨 Use bronchodilator preventively. Contact doctor.",
        "agricult":   "🚨 Stop work during hot hours. FFP2 mask required.",
    },
    "critique": {
        "enfants":    "🔴 DANGER — Do not go out. Close windows. Call doctor if symptoms.",
        "enceintes":  "🔴 DANGER — Strict confinement. Urgent medical consultation recommended.",
        "ages":       "🔴 DANGER — Stay confined. Activate emergency medical monitoring.",
        "asthma":     "🔴 CRITICAL DANGER — Emergency treatment. Call 15 if crisis.",
        "agricult":   "🔴 DANGER — Stop all outdoor work. Go out only if absolutely necessary.",
    },
}

def _vuln_section(snk, lang, th):
    """Affiche les recommandations populations vulnérables."""
    data = VULN_FR[snk] if lang == "fr" else VULN_EN[snk]
    pops = [
        ("👶", "Enfants < 18 ans"      if lang=="fr" else "Children < 18 yrs",  "enfants"),
        ("🤰", "Femmes enceintes"       if lang=="fr" else "Pregnant women",      "enceintes"),
        ("👴", "Personnes âgées"        if lang=="fr" else "Elderly",             "ages"),
        ("🫁", "Asthmatiques"           if lang=="fr" else "Asthmatics",          "asthma"),
        ("🌾", "Agriculteurs"           if lang=="fr" else "Farmers",             "agricult"),
    ]
    color_map = {"faible":th["green"],"modere":th["amber"],"eleve":th["coral"],"critique":th["red"]}
    col_color = color_map[snk]
    titre = "Recommandations · Populations vulnérables" if lang=="fr" else "Recommendations · Vulnerable populations"
    st.markdown(f"""
    <div style="margin-top:20px;padding:18px 20px;background:{th['bg_tertiary']};
                border:1px solid {col_color}33;border-left:4px solid {col_color};
                border-radius:12px;">
        <div style="font-size:12px;font-weight:600;color:{col_color};
                    text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px;">
            {titre}
        </div>
    """, unsafe_allow_html=True)
    cols = st.columns(len(pops))
    for col, (icon, label, key) in zip(cols, pops):
        with col:
            st.markdown(f"""
            <div style="background:{th['bg_elevated']};border:1px solid {th['border_soft']};
                        border-radius:10px;padding:12px 10px;height:100%;text-align:center;">
                <div style="font-size:22px;margin-bottom:6px;">{icon}</div>
                <div style="font-size:11px;font-weight:600;color:{col_color};
                            margin-bottom:8px;">{label}</div>
                <div style="font-size:11px;color:{th['text']};line-height:1.55;text-align:left;">
                    {data[key]}
                </div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _rec_content(profil, profil_map, snk, tkey, snc, snt, ctx, th, T):
    """Affiche le contenu de recommandation selon profil."""
    pk = profil_map.get(profil, "citizen")
    st.markdown(f"""
    <div style="background:{th['bg_tertiary']};border:1px solid {th['border_soft']};
                border-radius:12px;padding:20px;min-height:260px;">
        <div style="font-size:10px;text-transform:uppercase;letter-spacing:.1em;
                    color:{th['text3']};margin-bottom:14px;">
            {T['bloc5_rec_header']} · {profil} · {ctx['scope_label']}
        </div>
    """, unsafe_allow_html=True)

    if pk == "health":
        sk = _SNK_TO_STATUS[snk]
        st.markdown(f"""
        <div style="border-left:3px solid {snc};padding-left:16px;">
            <div style="font-size:16px;font-weight:600;color:{snc};margin-bottom:14px;">{T[sk]}</div>
            <div style="font-size:11px;color:{th['text3']};margin-bottom:2px;">{T['bloc5_med_label']}</div>
            <div style="font-size:13px;color:{th['text']};margin-bottom:10px;">{T[f'bloc5_med_{tkey}']}</div>
            <div style="font-size:11px;color:{th['text3']};margin-bottom:2px;">{T['bloc5_cons_label']}</div>
            <div style="font-size:13px;color:{th['text']};margin-bottom:10px;">
                {T[f'bloc5_cons_{tkey}']} · {ctx['scope_label']}
            </div>
            <div style="font-size:11px;color:{th['text3']};margin-bottom:2px;">{T['bloc5_action_label']}</div>
            <div style="font-size:13px;color:{th['text']};">{T[f'bloc5_action_{tkey}']}</div>
        </div>""", unsafe_allow_html=True)

    elif pk == "mayor":
        sk   = _SNK_TO_MAYOR[snk]
        acts = T[f"bloc5_mayor_{tkey}"]
        acts_html = "".join([
            f"<div style='padding:7px 0;border-bottom:1px solid {th['border_soft']};"
            f"font-size:13px;color:{th['text']};'>→ {a}</div>" for a in acts])
        st.markdown(f"""
        <div style="border-left:3px solid {snc};padding-left:16px;">
            <div style="font-size:16px;font-weight:600;color:{snc};margin-bottom:12px;">{T[sk]}</div>
            {acts_html}
        </div>""", unsafe_allow_html=True)

    elif pk == "researcher":
        msg = T[f"bloc5_researcher_{snk}"]
        st.markdown(f"""
        <div style="border-left:3px solid {snc};padding-left:16px;">
            <div style="font-size:14px;color:{th['text']};line-height:1.7;">
                {msg} · {ctx['scope_label']}
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        msg = T[f"bloc5_citizen_{snk}"]
        st.markdown(f"""
        <div style="border-left:3px solid {snc};padding-left:16px;">
            <div style="font-size:14px;color:{th['text']};line-height:1.7;">{msg}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render(profil):
    ctx  = get_context()
    df   = ctx["df"]; th = ctx["th"]; T = ctx["T"]
    lang = ctx["lang"]

    profil_map = {
        T["sidebar_profile_citizen"]:    "citizen",
        T["sidebar_profile_health"]:     "health",
        T["sidebar_profile_mayor"]:      "mayor",
        T["sidebar_profile_researcher"]: "researcher",
    }

    # Bannière
    cb1, cb2 = st.columns([3, 2])
    with cb1:
        st.markdown(f"""
        <div style="position:relative;border-radius:12px;overflow:hidden;height:175px;
                    border:1px solid rgba(249,115,22,0.22);margin-bottom:18px;">
            <img src="{IMAGES['sante_banner']}"
                 style="width:100%;height:100%;object-fit:cover;object-position:center 30%;
                        filter:saturate(0.60) brightness(0.52);"
                 onerror="this.style.opacity='0'"/>
            <div style="position:absolute;inset:0;
                        background:linear-gradient(to right,rgba(249,115,22,0.28),rgba(2,12,24,0.80));"></div>
            <div style="position:absolute;bottom:0;left:0;right:0;padding:16px 20px;">
                <div style="font-size:10px;color:{th['coral']};letter-spacing:.12em;
                            text-transform:uppercase;font-family:'DM Mono',monospace;margin-bottom:4px;">
                    {T['bloc5_label']}
                </div>
                <div style="font-size:18px;font-weight:600;color:#e0f2fe;">
                    {ctx['scope_label']}
                </div>
                <div style="font-size:12px;color:rgba(224,242,254,0.65);margin-top:3px;">
                    IRS : {ctx['irs_moy']:.3f} → {ctx['irs_label']} · {profil}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    with cb2:
        st.markdown(f"""
        <div style="background:{th['bg_tertiary']};border:1px solid rgba(249,115,22,0.18);
                    border-left:3px solid {th['coral']};border-radius:10px;
                    padding:14px 16px;height:175px;margin-bottom:18px;
                    display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:12px;font-weight:500;color:{th['coral']};margin-bottom:8px;">
                {T['bloc5_innovation']}
            </div>
            <div style="font-size:12px;color:{th['text2']};line-height:1.7;">
                {T['bloc5_innovation_desc']}
            </div>
        </div>""", unsafe_allow_html=True)

    if len(df) == 0:
        empty_state(T, th)
        return

    # ══ 2 SOUS-ONGLETS ═══════════════════════════════════════════════════════
    tab_real_lbl = ("📊 Données réelles · " + ctx["scope_annees"]
                    if lang == "fr" else
                    "📊 Real data · " + ctx["scope_annees"])
    tab_sim_lbl  = ("🎛️ Simulateur IRS"
                    if lang == "fr" else
                    "🎛️ HRI Simulator")

    sub1, sub2 = st.tabs([tab_real_lbl, tab_sim_lbl])

    # ── Sous-onglet 1 : données réelles ──────────────────────────────────────
    with sub1:
        # IRS calculé sur les données réelles filtrées
        irs_real = float(ctx["irs_moy"])
        snc_r, snt_r, snk_r = irs_level(irs_real, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
        tkey_r = _SNK_TO_KEY[snk_r]

        st.markdown(f"""
        <div style="background:{th['bg_elevated']};border:2px solid {snc_r};
                    border-radius:12px;padding:14px 20px;margin-bottom:18px;
                    display:flex;align-items:center;gap:20px;">
            <div style="text-align:center;min-width:90px;">
                <div style="font-size:11px;color:{th['text3']};margin-bottom:3px;">
                    {'IRS moyen réel' if lang=='fr' else 'Real avg HRI'}
                </div>
                <div style="font-size:30px;font-weight:700;color:{snc_r};">{irs_real:.3f}</div>
                <div style="font-size:14px;margin-top:4px;">{snt_r}</div>
            </div>
            <div style="flex:1;border-left:1px solid {th['border_soft']};padding-left:20px;">
                <div style="display:flex;gap:20px;flex-wrap:wrap;">
                    <div>
                        <div style="font-size:10px;color:{th['text3']};margin-bottom:2px;">PM2.5 moy.</div>
                        <div style="font-size:16px;font-weight:600;
                                    color:{th['red'] if ctx['pm25_moy']>15 else th['green']};">
                            {ctx['pm25_moy']:.1f} µg/m³
                        </div>
                    </div>
                    <div>
                        <div style="font-size:10px;color:{th['text3']};margin-bottom:2px;">p50 · p75 · p90</div>
                        <div style="font-size:13px;color:{th['text2']};font-family:'DM Mono',monospace;">
                            {ctx['p50']:.3f} · {ctx['p75']:.3f} · {ctx['p90']:.3f}
                        </div>
                    </div>
                    <div>
                        <div style="font-size:10px;color:{th['text3']};margin-bottom:2px;">
                            {'Période' if lang=='fr' else 'Period'}
                        </div>
                        <div style="font-size:13px;color:{th['text2']};">{ctx['scope_label']}</div>
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        _rec_content(profil, profil_map, snk_r, tkey_r, snc_r, snt_r, ctx, th, T)
        _vuln_section(snk_r, lang, th)

    # ── Sous-onglet 2 : simulateur ────────────────────────────────────────────
    with sub2:
        col_sl, col_rec = st.columns([1, 2])

        with col_sl:
            irs_v = st.slider(
                T["bloc5_slider_label"], 0.0, 1.0,
                float(ctx["irs_moy"]), 0.001, key="dec_irs",
            )
            snc_s, snt_s, snk_s = irs_level(irs_v, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
            tkey_s = _SNK_TO_KEY[snk_s]

            st.markdown(f"""
            <div style="background:{th['bg_elevated']};border:2px solid {snc_s};
                        border-radius:12px;padding:18px;text-align:center;margin-top:10px;">
                <div style="font-size:34px;font-weight:700;color:{snc_s};">{irs_v:.3f}</div>
                <div style="font-size:18px;margin:8px 0;">{snt_s}</div>
                <div style="font-size:10px;color:{th['text3']};font-family:'DM Mono',monospace;line-height:1.9;">
                    p50 = {ctx['p50']:.3f}<br>p75 = {ctx['p75']:.3f}<br>p90 = {ctx['p90']:.3f}<br>
                    <span style="color:{th['text2']};">
                        avg {ctx['scope_annees']} : {ctx['irs_moy']:.3f}
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            img_card(IMAGES["sante_side"], 100,
                     T["bloc5_label"].split("—")[0].strip(), "Africa", th, tint_hex="#fb923c")

        with col_rec:
            _rec_content(profil, profil_map, snk_s, tkey_s, snc_s, snt_s, ctx, th, T)

        _vuln_section(snk_s, lang, th)

    sources_bar(f"{T['sources_who']} · ACP 42 villes · Ceccherini 2017", th)
