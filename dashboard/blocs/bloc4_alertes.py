"""blocs/bloc4_alertes.py — Alertes dynamiques (High-Impact Fluid Redesigned)"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils import get_context, banner, sources_bar, empty_state, irs_level
from assets import IMAGES

def _render_irs_gauge(irs, ctx, th, T):
    """Affiche un indicateur en jauge (conteur de voiture) pour l'IRS."""
    p50, p75, p90 = ctx["p50"], ctx["p75"], ctx["p90"]
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = irs,
        domain = {'x': [0, 1], 'y': [0, 1]},
        number = {'font': {'size': 42, 'color': th['text'], 'weight': 'bold'}, 'valueformat': ".3f"},
        gauge = {
            'axis': {
                'range': [0, 1], 
                'tickwidth': 3, 
                'tickcolor': th['text'],
                'tickvals': [0, p50, p75, p90, 1],
                'ticktext': ["0", f"<b>{p50:.2f}</b>", f"<b>{p75:.2f}</b>", f"<b>{p90:.2f}</b>", "1"],
                'tickmode': 'array',
                'tickfont': {'size': 13, 'color': th['text'], 'family': 'Arial Black, sans-serif'}
            },
            'bar': {'color': th['text'], 'thickness': 0.15},
            'bgcolor': "rgba(0,0,0,0.05)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, p50],   'color': th["green"]},
                {'range': [p50, p75], 'color': th["amber"]},
                {'range': [p75, p90], 'color': th["coral"]},
                {'range': [p90, 1],   'color': th["red"]},
            ],
            'threshold': {
                'line': {'color': "#fff", 'width': 4},
                'thickness': 0.8,
                'value': irs
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor = "rgba(0,0,0,0)",
        font = {'color': th['text2'], 'family': "Inter"},
        height = 240,
        margin = dict(l=65, r=65, t=50, b=20)
    )
    return fig

def render(profil):
    ctx = get_context()
    df_brut = ctx["df_brut"]
    th = ctx["th"]
    T = ctx["T"]
    p50, p75, p90 = ctx["p50"], ctx["p75"], ctx["p90"]

    # ── Header & Sélecteur (Synchronisé avec bloc3) ───────────────────────────
    ch1, ch2 = st.columns([2.4, 1])
    with ch1:
        banner(IMAGES["alertes_banner"], 120,
               T['bloc4_label'],
               profil.upper(), th,
               accent=th["teal"], tint_hex="#00d4b1", tint_strength=0.28)


    with ch2:
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
    st.markdown(f"""
        <div style="text-align:center; margin-bottom:-45px;">
            <div style="font-size:26px; font-weight:950; color:{th['text']}; 
                        letter-spacing:0.1em; text-transform:uppercase;
                        text-shadow: 0px 4px 12px {th['text']}33;">
                NIVEAU D'IRS
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(_render_irs_gauge(irs_val, ctx, th, T), width='stretch', config={'displayModeBar': False}, key="gauge_v4_fluid")

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
