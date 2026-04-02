"""blocs/bloc5_decision.py — Décision santé · par ville · données du jour"""
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
        "enfants":  "✅ Activités extérieures normales autorisées.",
        "enceintes":"✅ Sorties normales. Aération intérieure recommandée.",
        "ages":     "✅ Activité physique légère possible en extérieur.",
        "asthma":   "✅ Gardez votre bronchodilatateur à portée par précaution.",
        "agricult": "✅ Travaux agricoles sans restriction particulière.",
    },
    "modere": {
        "enfants":  "⚠️ Réduire les jeux intensifs en plein air. Favoriser les activités intérieures.",
        "enceintes":"⚠️ Limiter les sorties prolongées. Éviter les axes très fréquentés.",
        "ages":     "⚠️ Éviter les efforts physiques en extérieur. Surveiller la respiration.",
        "asthma":   "⚠️ Avoir le bronchodilatateur accessible. Limiter l'exposition.",
        "agricult": "⚠️ Porter un masque FFP2 lors des travaux. Faire des pauses fréquentes.",
    },
    "eleve": {
        "enfants":  "🚨 Annuler les cours de sport en extérieur. Garder les enfants à l'intérieur.",
        "enceintes":"🚨 Rester à l'intérieur. Consulter un médecin si gêne respiratoire.",
        "ages":     "🚨 Rester à l'intérieur. Prendre les médicaments préventifs.",
        "asthma":   "🚨 Utiliser le bronchodilatateur en prévention. Contacter le médecin.",
        "agricult": "🚨 Interrompre les travaux aux heures chaudes. Masque FFP2 obligatoire.",
    },
    "critique": {
        "enfants":  "🔴 DANGER — Ne pas sortir. Fermer fenêtres. Appeler le médecin si symptômes.",
        "enceintes":"🔴 DANGER — Confinement strict. Consultation médicale urgente recommandée.",
        "ages":     "🔴 DANGER — Rester confiné. Activer le suivi médical d'urgence.",
        "asthma":   "🔴 DANGER CRITIQUE — Traitement d'urgence. Appeler le 15 si crise.",
        "agricult": "🔴 DANGER — Cesser tout travail extérieur. Ne sortir qu'en cas d'absolue nécessité.",
    },
}
VULN_EN = {
    "faible": {
        "enfants":  "✅ Normal outdoor activities allowed.",
        "enceintes":"✅ Normal outings. Indoor ventilation recommended.",
        "ages":     "✅ Light physical activity possible outdoors.",
        "asthma":   "✅ Keep bronchodilator handy as precaution.",
        "agricult": "✅ Agricultural work without particular restriction.",
    },
    "modere": {
        "enfants":  "⚠️ Reduce intense outdoor play. Prefer indoor activities.",
        "enceintes":"⚠️ Limit prolonged outings. Avoid busy roads.",
        "ages":     "⚠️ Avoid physical exertion outdoors. Monitor breathing.",
        "asthma":   "⚠️ Keep bronchodilator accessible. Limit exposure.",
        "agricult": "⚠️ Wear FFP2 mask during work. Take frequent breaks.",
    },
    "eleve": {
        "enfants":  "🚨 Cancel outdoor sports. Keep children indoors.",
        "enceintes":"🚨 Stay indoors. See doctor if breathing difficulty.",
        "ages":     "🚨 Stay indoors. Take preventive medications.",
        "asthma":   "🚨 Use bronchodilator preventively. Contact doctor.",
        "agricult": "🚨 Stop work during hot hours. FFP2 mask required.",
    },
    "critique": {
        "enfants":  "🔴 DANGER — Do not go out. Close windows. Call doctor if symptoms.",
        "enceintes":"🔴 DANGER — Strict confinement. Urgent medical consultation recommended.",
        "ages":     "🔴 DANGER — Stay confined. Activate emergency medical monitoring.",
        "asthma":   "🔴 CRITICAL DANGER — Emergency treatment. Call 15 if crisis.",
        "agricult": "🔴 DANGER — Stop all outdoor work. Go out only if absolutely necessary.",
    },
}

def _vuln_section(snk, lang, th):
    data = VULN_FR[snk] if lang == "fr" else VULN_EN[snk]
    pops = [
        ("👶", "Enfants < 18 ans"  if lang == "fr" else "Children < 18 yrs",  "enfants"),
        ("🤰", "Femmes enceintes"  if lang == "fr" else "Pregnant women",      "enceintes"),
        ("👴", "Personnes âgées"   if lang == "fr" else "Elderly",             "ages"),
        ("🫁", "Asthmatiques"      if lang == "fr" else "Asthmatics",          "asthma"),
        ("🌾", "Agriculteurs"      if lang == "fr" else "Farmers",             "agricult"),
    ]
    color_map = {"faible": th["green"], "modere": th["amber"],
                 "eleve": th["coral"], "critique": th["red"]}
    col_color = color_map[snk]
    titre = "Recommandations · Populations vulnérables" if lang == "fr" else "Recommendations · Vulnerable populations"
    st.markdown(
        f'<div style="margin-top:20px;padding:18px 20px;background:{th["bg_tertiary"]};'
        f'border:1px solid {col_color}33;border-left:4px solid {col_color};border-radius:12px;">'
        f'<div style="font-size:12px;font-weight:600;color:{col_color};'
        f'text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px;">{titre}</div>',
        unsafe_allow_html=True
    )
    cols = st.columns(len(pops))
    for col, (icon, label, key) in zip(cols, pops):
        with col:
            st.markdown(
                f'<div style="background:{th["bg_elevated"]};border:1px solid {th["border_soft"]};'
                f'border-radius:10px;padding:12px 10px;height:100%;text-align:center;">'
                f'<div style="font-size:22px;margin-bottom:6px;">{icon}</div>'
                f'<div style="font-size:11px;font-weight:600;color:{col_color};margin-bottom:8px;">{label}</div>'
                f'<div style="font-size:11px;color:{th["text"]};line-height:1.55;text-align:left;">'
                f'{data[key]}</div></div>',
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)


def _rec_content(profil, profil_map, snk, tkey, snc, snt, ctx, th, T, scope_label):
    pk = profil_map.get(profil, "citizen")
    st.markdown(
        f'<div style="background:{th["bg_tertiary"]};border:1px solid {th["border_soft"]};'
        f'border-radius:10px;padding:12px 16px;">'
        f'<div style="font-size:9px;text-transform:uppercase;letter-spacing:.1em;'
        f'color:{th["text3"]};margin-bottom:10px;">'
        f'{T["bloc5_rec_header"]} · {profil} · {scope_label}</div>',
        unsafe_allow_html=True
    )

    if pk == "health":
        sk = _SNK_TO_STATUS[snk]
        st.markdown(
            f'<div style="border-left:3px solid {snc};padding-left:16px;">'
            f'<div style="font-size:16px;font-weight:600;color:{snc};margin-bottom:14px;">{T[sk]}</div>'
            f'<div style="font-size:11px;color:{th["text3"]};margin-bottom:2px;">{T["bloc5_med_label"]}</div>'
            f'<div style="font-size:13px;color:{th["text"]};margin-bottom:10px;">{T[f"bloc5_med_{tkey}"]}</div>'
            f'<div style="font-size:11px;color:{th["text3"]};margin-bottom:2px;">{T["bloc5_cons_label"]}</div>'
            f'<div style="font-size:13px;color:{th["text"]};margin-bottom:10px;">'
            f'{T[f"bloc5_cons_{tkey}"]} · {scope_label}</div>'
            f'<div style="font-size:11px;color:{th["text3"]};margin-bottom:2px;">{T["bloc5_action_label"]}</div>'
            f'<div style="font-size:13px;color:{th["text"]};">{T[f"bloc5_action_{tkey}"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    elif pk == "mayor":
        sk       = _SNK_TO_MAYOR[snk]
        acts     = T[f"bloc5_mayor_{tkey}"]
        acts_html = "".join([
            f'<div style="padding:7px 0;border-bottom:1px solid {th["border_soft"]};'
            f'font-size:13px;color:{th["text"]};">→ {a}</div>'
            for a in acts
        ])
        st.markdown(
            f'<div style="border-left:3px solid {snc};padding-left:16px;">'
            f'<div style="font-size:16px;font-weight:600;color:{snc};margin-bottom:14px;">{T[sk]}</div>'
            f'{acts_html}</div>',
            unsafe_allow_html=True
        )

    else:
        sk  = _SNK_TO_STATUS[snk]
        msg = T.get(f"bloc4_msg_{snk}_{pk}", T.get(f"bloc4_msg_{snk}_citizen", "—"))
        st.markdown(
            f'<div style="border-left:3px solid {snc};padding-left:16px;">'
            f'<div style="font-size:16px;font-weight:600;color:{snc};margin-bottom:12px;">{T[sk]}</div>'
            f'<div style="font-size:13px;color:{th["text"]};line-height:1.7;">{msg}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render(profil):
    ctx  = get_context()
    df   = ctx["df_brut"]
    th   = ctx["th"]
    T    = ctx["T"]
    lang = ctx["lang"]

    profil_map = {
        T["sidebar_profile_citizen"]:    "citizen",
        T["sidebar_profile_health"]:     "health",
        T["sidebar_profile_mayor"]:      "mayor",
        T["sidebar_profile_researcher"]: "researcher",
    }

    # ── Labels sans backslash ─────────────────────────────────────────────────
    dec_title    = "Recommandations par ville · Données du jour" if lang == "fr" else "City recommendations · Today's data"
    vs_lbl       = "vs seuil OMS" if lang == "fr" else "vs WHO threshold"
    periode_lbl  = "Période" if lang == "fr" else "Period"
    poll_dom_lbl = "Polluant dominant" if lang == "fr" else "Dominant pollutant"
    choisir_lbl  = "Choisir une ville" if lang == "fr" else "Choose a city"
    auj_lbl      = "📅 Aujourd'hui" if lang == "fr" else "📅 Today"
    hist_lbl     = "📊 Historique" if lang == "fr" else "📊 Historical"
    sim_lbl      = "🎛️ Simulateur IRS" if lang == "fr" else "🎛️ HRI Simulator"
    irs_moy_lbl  = "IRS moyen réel" if lang == "fr" else "Real avg HRI"
    data_lbl     = "Données réelles" if lang == "fr" else "Real data"

    # ── Bannière ──────────────────────────────────────────────────────────────
    cb1, cb2 = st.columns([3, 2])
    with cb1:
        st.markdown(
            f'<div style="position:relative;border-radius:12px;overflow:hidden;height:175px;'
            f'border:1px solid rgba(249,115,22,0.22);margin-bottom:18px;">'
            f'<img src="{IMAGES["sante_banner"]}"'
            f' style="width:100%;height:100%;object-fit:cover;object-position:center 30%;'
            f'filter:saturate(0.60) brightness(0.52);" onerror="this.style.opacity=\'0\'"/>'
            f'<div style="position:absolute;inset:0;'
            f'background:linear-gradient(to right,rgba(249,115,22,0.28),rgba(2,12,24,0.80));"></div>'
            f'<div style="position:absolute;bottom:0;left:0;right:0;padding:16px 20px;">'
            f'<div style="font-size:10px;color:{th["coral"]};letter-spacing:.12em;'
            f'text-transform:uppercase;font-family:DM Mono,monospace;margin-bottom:4px;">'
            f'{T["bloc5_label"]}</div>'
            f'<div style="font-size:18px;font-weight:600;color:#e0f2fe;">{dec_title}</div>'
            f'<div style="font-size:12px;color:rgba(224,242,254,0.65);margin-top:3px;">{profil}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
    with cb2:
        st.markdown(
            f'<div style="background:{th["bg_tertiary"]};border:1px solid rgba(249,115,22,0.18);'
            f'border-left:3px solid {th["coral"]};border-radius:10px;'
            f'padding:14px 16px;height:175px;margin-bottom:18px;'
            f'display:flex;flex-direction:column;justify-content:center;">'
            f'<div style="font-size:12px;font-weight:500;color:{th["coral"]};margin-bottom:8px;">'
            f'{T["bloc5_innovation"]}</div>'
            f'<div style="font-size:12px;color:{th["text2"]};line-height:1.7;">'
            f'{T["bloc5_innovation_desc"]}</div></div>',
            unsafe_allow_html=True
        )

    if len(df) == 0:
        empty_state(T, th)
        return

    # ── Sélecteur de ville + mode ─────────────────────────────────────────────
    col_v, col_m = st.columns([2, 1])
    with col_v:
        villes_dispo = sorted(df["ville"].unique().tolist())
        ville_dec    = st.selectbox(
            "🏙️ " + choisir_lbl,
            villes_dispo,
            key="ville_decision"
        )
    with col_m:
        mode = st.radio(
            "Mode",
            [auj_lbl, hist_lbl],
            horizontal=True,
            key="dec_mode"
        )
    mode_today = "Aujourd'hui" in mode or "Today" in mode

    # ── Filtrer selon ville + mode ────────────────────────────────────────────
    if mode_today:
        date_max    = df["date"].max()
        df_ville    = df[(df["ville"] == ville_dec) & (df["date"] == date_max)]
        scope_label = f"{ville_dec} · {date_max.date()}"
    else:
        an_min, an_max_sel = st.session_state.get(
            "annee_sel",
            (int(df["date"].dt.year.min()), int(df["date"].dt.year.max()))
        )
        df_ville = df[
            (df["ville"] == ville_dec) &
            (df["date"].dt.year >= an_min) &
            (df["date"].dt.year <= an_max_sel)
        ]
        scope_label = f"{ville_dec} · {an_min}–{an_max_sel}"

    if len(df_ville) == 0:
        empty_state(T, th)
        return

    # ── Calcul IRS ville ──────────────────────────────────────────────────────
    pm25_ville = float(df_ville["pm2_5_moyen"].mean())
    irs_ville  = float(df_ville["IRS"].mean())
    snc, snt, snk = irs_level(irs_ville, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
    tkey = _SNK_TO_KEY[snk]

    # Polluant dominant
    if "polluant_dominant" in df_ville.columns and len(df_ville) > 0:
        poll_dom_val = df_ville["polluant_dominant"].mode()[0]
    else:
        poll_dom_val = "PM2.5"

    # Couleur PM2.5
    pm25_color = th["red"] if pm25_ville > 15 else th["green"]

    # ── Carte de situation ────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:{th["bg_elevated"]};border:2px solid {snc};'
        f'border-radius:12px;padding:16px 20px;margin-bottom:20px;'
        f'display:flex;align-items:center;gap:20px;">'
        f'<div style="text-align:center;min-width:100px;">'
        f'<div style="font-size:11px;color:{th["text3"]};margin-bottom:3px;">📍 {ville_dec}</div>'
        f'<div style="font-size:30px;font-weight:700;color:{snc};">{irs_ville:.3f}</div>'
        f'<div style="font-size:14px;margin-top:4px;">{snt}</div>'
        f'</div>'
        f'<div style="flex:1;border-left:1px solid {th["border_soft"]};padding-left:20px;">'
        f'<div style="display:flex;gap:24px;flex-wrap:wrap;">'
        f'<div>'
        f'<div style="font-size:10px;color:{th["text3"]};margin-bottom:2px;">PM2.5</div>'
        f'<div style="font-size:18px;font-weight:600;color:{pm25_color};">{pm25_ville:.1f} µg/m³</div>'
        f'</div>'
        f'<div>'
        f'<div style="font-size:10px;color:{th["text3"]};margin-bottom:2px;">{vs_lbl}</div>'
        f'<div style="font-size:16px;font-weight:600;color:{pm25_color};">{pm25_ville/15:.1f}x</div>'
        f'</div>'
        f'<div>'
        f'<div style="font-size:10px;color:{th["text3"]};margin-bottom:2px;">{periode_lbl}</div>'
        f'<div style="font-size:13px;color:{th["text2"]};">{scope_label}</div>'
        f'</div>'
        f'<div>'
        f'<div style="font-size:10px;color:{th["text3"]};margin-bottom:2px;">{poll_dom_lbl}</div>'
        f'<div style="font-size:13px;color:{th["blue"]};font-weight:600;">{poll_dom_val}</div>'
        f'</div>'
        f'</div></div></div>',
        unsafe_allow_html=True
    )

    # ── 2 sous-onglets ────────────────────────────────────────────────────────
    tab_real_lbl = f"📊 {data_lbl} · {scope_label}"

    sub1, sub2 = st.tabs([tab_real_lbl, sim_lbl])

    with sub1:
        _rec_content(profil, profil_map, snk, tkey, snc, snt, ctx, th, T, scope_label)
        _vuln_section(snk, lang, th)

    with sub2:
        col_sl, col_rec = st.columns([1, 2])
        with col_sl:
            irs_v = st.slider(
                T["bloc5_slider_label"], 0.0, 1.0,
                float(irs_ville), 0.001, key="dec_irs"
            )
            snc_s, snt_s, snk_s = irs_level(irs_v, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
            tkey_s = _SNK_TO_KEY[snk_s]
            st.markdown(
                f'<div style="background:{th["bg_elevated"]};border:2px solid {snc_s};'
                f'border-radius:12px;padding:18px;text-align:center;margin-top:10px;">'
                f'<div style="font-size:34px;font-weight:700;color:{snc_s};">{irs_v:.3f}</div>'
                f'<div style="font-size:18px;margin:8px 0;">{snt_s}</div>'
                f'<div style="font-size:10px;color:{th["text3"]};font-family:DM Mono,monospace;line-height:1.9;">'
                f'p50 = {ctx["p50"]:.3f}<br>p75 = {ctx["p75"]:.3f}<br>p90 = {ctx["p90"]:.3f}'
                f'</div></div>',
                unsafe_allow_html=True
            )
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            img_card(
                IMAGES["sante_side"], 100,
                T["bloc5_label"].split("—")[0].strip(), "Africa",
                th, tint_hex="#fb923c"
            )
        with col_rec:
            _rec_content(profil, profil_map, snk_s, tkey_s, snc_s, snt_s, ctx, th, T, scope_label)
        _vuln_section(snk_s, lang, th)

    sources_bar(f"{T['sources_who']} · ACP 40 villes · Chen & Hoek (2020)", th)
