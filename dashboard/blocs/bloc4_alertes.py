"""blocs/bloc4_alertes.py — Alertes dynamiques (High-Impact Fluid Redesigned)"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components
from utils import get_context, banner, sources_bar, empty_state, irs_level
from assets import IMAGES
def _render_irs_gauge_animated(irs, ctx, th, T):
    """Affiche une jauge propre, mathématiquement exacte, sans image de fond."""
    # Seuils réels
    s1, s2, s3 = 0.08, 0.13, 0.18
    
    # Couleurs exactes
    c_green = "#10b981"
    c_amber = "#f59e0b"
    c_coral = "#f97316"
    c_red   = "#ef4444"
    
    html_code = f"""
    <div id="gauge-container" style="width: 100%; display: flex; justify-content: center; align-items: center; background: transparent;">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@900&display=swap');
            body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
            #main-box {{ 
                position: relative; 
                width: 550px; height: 320px; 
                background: transparent;
                display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
            }}
            .gauge-svg {{ width: 500px; height: 260px; margin-top: 10px; }}
            .irs-value {{ font-size: 52px; font-family: 'DM Serif Display', serif; fill: {th['text']}; text-anchor: middle; }}
            .tick-text {{ font-size: 15px; font-weight: 900; fill: {th['text']}; font-family: 'Inter', sans-serif; }}
            .needle {{ transition: transform 1.5s cubic-bezier(0.19, 1, 0.22, 1); transform-origin: 250px 210px; }}
            .tick-line {{ stroke: {th['text']}; stroke-width: 1.5; opacity: 0.6; }}
        </style>
        
        <div id="main-box">
            <div style="font-family:'Inter',sans-serif; color:{th['text']}; font-size:24px; font-weight:900; letter-spacing:0.15em; margin-top:25px; text-transform:uppercase;">NIVEAU D'IRS</div>
            <svg class="gauge-svg" viewBox="0 0 500 260">
                <!-- Segments Arcs (Mathématiquement proportionnels) -->
                <path id="arc-green"  fill="none" stroke="{c_green}" stroke-width="50" />
                <path id="arc-amber"  fill="none" stroke="{c_amber}" stroke-width="50" />
                <path id="arc-coral"  fill="none" stroke="{c_coral}" stroke-width="50" />
                <path id="arc-red"    fill="none" stroke="{c_red}"   stroke-width="50" />

                <!-- Valeur centrale -->
                <text x="250" y="195" class="irs-value" id="irs-text">0.000</text>

                <!-- Ticks Group (Étiquettes + Tirets) -->
                <g id="ticks-group"></g>

                <!-- Aiguille (Barre blanche style "T-Cut") - Positionnée dans l'arc (Rayon ~150) -->
                <g id="needle-group" class="needle" style="transform: rotate(-90deg);">
                    <rect x="247" y="35" width="6" height="50" fill="{th['text']}" filter="drop-shadow(0 0 5px {th['text']}55)" />
                </g>
            </svg>
        </div>

        <script>
            (function() {{
                const R = 150; // Rayon de l'arc
                const CX = 250; const CY = 210;
                
                function getPoint(angle, radius) {{
                    const rad = angle * Math.PI / 180;
                    return (CX + radius * Math.cos(Math.PI - rad)) + " " + (CY - radius * Math.sin(Math.PI - rad));
                }}
                
                function setArc(id, startAngle, endAngle) {{
                    const d = "M " + getPoint(startAngle, R) + " A " + R + " " + R + " 0 0 1 " + getPoint(endAngle, R);
                    document.getElementById(id).setAttribute("d", d);
                }}

                const s1 = {s1}; const s2 = {s2}; const s3 = {s3};
                
                // Mappage réel sur 180 degrés
                setArc("arc-green", 0, s1 * 180);
                setArc("arc-amber", s1 * 180, s2 * 180);
                setArc("arc-coral", s2 * 180, s3 * 180);
                setArc("arc-red", s3 * 180, 180);

                // Ticks
                const ticks = [
                    {{val: 0, angle: 0}},
                    {{val: s1, angle: s1 * 180}},
                    {{val: s2, angle: s2 * 180}},
                    {{val: s3, angle: s3 * 180}},
                    {{val: 1, angle: 180}}
                ];
                
                const tg = document.getElementById("ticks-group");
                ticks.forEach(t => {{
                    // Ligne de liaison (le petit tiret)
                    const pStart = getPoint(t.angle, R + 25);
                    const pEnd = getPoint(t.angle, R + 35);
                    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    line.setAttribute("x1", pStart.split(" ")[0]); line.setAttribute("y1", pStart.split(" ")[1]);
                    line.setAttribute("x2", pEnd.split(" ")[0]); line.setAttribute("y2", pEnd.split(" ")[1]);
                    line.setAttribute("class", "tick-line");
                    tg.appendChild(line);

                    // Texte
                    const pTxt = getPoint(t.angle, R + 55);
                    const txt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    txt.setAttribute("x", pTxt.split(" ")[0]);
                    txt.setAttribute("y", pTxt.split(" ")[1]);
                    txt.setAttribute("class", "tick-text");
                    txt.setAttribute("text-anchor", t.angle > 110 ? "start" : t.angle < 70 ? "end" : "middle");
                    txt.setAttribute("dominant-baseline", "middle");
                    txt.textContent = t.val === 0 ? "0" : (t.val === 1 ? "1" : t.val.toFixed(2));
                    tg.appendChild(txt);
                }});

                const targetIrs = {irs};
                const irsText = document.getElementById("irs-text");
                const needle = document.getElementById("needle-group");
                
                let start = null;
                function step(ts) {{
                    if (!start) start = ts;
                    const p = Math.min((ts - start) / 1800, 1);
                    const ease = 1 - Math.pow(1 - p, 4);
                    irsText.textContent = (ease * targetIrs).toFixed(3);
                    needle.style.transform = "rotate(" + ((ease * targetIrs * 180) - 90) + "deg)";
                    if (p < 1) requestAnimationFrame(step);
                }}
                requestAnimationFrame(step);
            }})();
        </script>
    </div>
    """
    components.html(html_code, height=340)


def render(profil):
    ctx = get_context()
    df_brut = ctx["df_brut"]
    th = ctx["th"]
    T = ctx["T"]
    p50, p75, p90 = ctx["p50"], ctx["p75"], ctx["p90"]

    # ── Header & Sélecteurs ───────────────────────────
    c1, c2, c3 = st.columns([2.6, 0.7, 0.7])
    with c1:
        banner(IMAGES["alertes_banner"], 120,
               T['bloc4_label'],
               profil.upper(), th,
               accent=th["teal"], tint_hex="#00d4b1", tint_strength=0.28)

    with c2:
        st.markdown('<div style="margin-top:34px;"></div>', unsafe_allow_html=True)
        profil_options = [
            T["sidebar_profile_citizen"],
            T["sidebar_profile_health"],
            T["sidebar_profile_mayor"],
            T["sidebar_profile_researcher"],
        ]
        p_lbl = ":material/person: " + ("**MON PROFIL :**" if ctx["lang"] == "fr" else "**MY PROFILE :**")
        
        def _update_profil_4():
            st.session_state["global_profil"] = st.session_state["profil_sel_4"]

        if st.session_state.get("profil_sel_4") != profil:
            st.session_state["profil_sel_4"] = profil
            
        st.selectbox(p_lbl, profil_options, key="profil_sel_4", on_change=_update_profil_4)

    with c3:
        st.markdown('<div style="margin-top:34px;"></div>', unsafe_allow_html=True)
        villes = sorted(df_brut["ville"].unique().tolist())
        sel_lbl = ":material/location_on: " + ("**SÉLECTIONNER UNE VILLE :**" if ctx["lang"] == "fr" else "**SELECT A CITY :**")
        ville_sel = st.selectbox(sel_lbl, villes, key="v4_city_split_header")

    # Récupérer la période Sidebar
    an_min, an_max = st.session_state.get("annee_sel", (int(df_brut["date"].dt.year.min()), int(df_brut["date"].dt.year.max())))
    df_alert = df_brut[(df_brut["ville"] == ville_sel) & (df_brut["date"].dt.year >= an_min) & (df_brut["date"].dt.year <= an_max)]
    
    if len(df_alert) == 0:
        st.error("⚠️ AUCUNE DONNÉE DISPONIBLE."); return

    irs_val = float(df_alert["IRS"].mean())
    snc, snt, snk = irs_level(irs_val, p50, p75, p90, T, th)

    # ── Jauge de Risque (Prend toute la largeur ou large centré) ─────────────
    # Le titre est désormais inclus dans la jauge pour un meilleur contrôle du design
    _render_irs_gauge_animated(irs_val, ctx, th, T)

    # ── Matrice des Risques (Structure originale préservée) ──────────────────
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    
    # Définition des icônes SVG pour chaque niveau
    icon_check = f'<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{th["green"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
    icon_warn  = f'<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{th["amber"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    icon_siren = f'<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{th["coral"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 18v-6a5 5 0 1 1 10 0v6"/><path d="M5 21h14"/><path d="M21 13h2"/><path d="M1 13h2"/><path d="M22 5l-2 2"/><path d="M2 5l2 2"/><path d="M11 2h2"/><path d="M12 7v5"/><path d="M12 17v2"/></svg>'
    icon_crit  = f'<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="{th["red"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'

    niveaux = [
        {"nk":"faible",   "range": f"IRS < {p50:.3f}",           "icon":icon_check,"lbl":T["level_faible"],   "c":th["green"],"bg":"rgba(16,185,129,0.12)"},
        {"nk":"modere",   "icon":icon_warn,  "lbl":T["level_modere"],   "c":th["amber"],"bg":"rgba(245,158,11,0.12)"},
        {"nk":"eleve",    "icon":icon_siren, "lbl":T["level_eleve"],    "c":th["coral"],"bg":"rgba(249,115,22,0.12)"},
        {"nk":"critique", "icon":icon_crit,  "lbl":T["level_critique"], "c":th["red"],  "bg":"rgba(239,68,68,0.14)"},
    ]

    pk = "citizen"
    if profil == T["sidebar_profile_health"]:     pk = "health"
    elif profil == T["sidebar_profile_mayor"]:      pk = "mayor"
    elif profil == T["sidebar_profile_researcher"]: pk = "researcher"

    cols = st.columns(4)
    for i, niv in enumerate(niveaux):
        msg = T.get(f"bloc4_msg_{niv['nk']}_{pk}", "—")
        actif = (niv["nk"] == snk)
        
        brd_style = f"4px solid {niv['c']}" if actif else f"1px solid {th['border_soft']}"
        opacity = "1.0" if actif else "0.80"
        scale = "scale(1.05)" if actif else "scale(1.0)"
        shadow = f"0 15px 45px {niv['c']}55" if actif else "0 4px 15px rgba(0,0,0,0.1)"

        # Petite icône pour accompagner le message
        icon_small = niv["icon"].replace('width="32"','width="16"').replace('height="32"','height="16"').replace('stroke-width="2.5"','stroke-width="3"')

        with cols[i]:
            st.markdown(f"""
            <div style="background:{niv['bg']};border:{brd_style};border-radius:12px;
                        padding:20px 15px;height:230px;display:flex;flex-direction:column;
                        opacity:{opacity};transform:{scale};box-shadow:{shadow};transition:all 0.4s ease;">
                <div style="margin-bottom:12px;">{niv['icon']}</div>
                <div style="font-size:14px;font-weight:950;color:{niv['c']};
                            letter-spacing:.1em;margin-bottom:8px;text-transform:uppercase;">{niv['lbl']}</div>
                <div style="font-size:12px;color:{th['text']};line-height:1.5;flex:1;font-weight:800;overflow:hidden;display:flex;align-items:flex-start;gap:6px;">
                    <span style="margin-top:2px; flex-shrink:0;">{icon_small}</span>
                    <span>{msg}</span>
                </div>
                {f'<div style="font-size:10px;background:{niv["c"]};color:#fff;border-radius:6px;padding:4px 10px;width:fit-content;margin-top:10px;font-weight:950;letter-spacing:0.5px;text-transform:uppercase;">Statut Ville</div>' if actif else ""}
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    # Note : Sources et Diagnostic Expert supprimés
