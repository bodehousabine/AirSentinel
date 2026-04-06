"""
app.py — AirSentinel Cameroun
Page d'accueil → Dashboard · Thème/Langue · Chatbox IA.
"""
import sys
import os
_dashboard_dir = os.path.dirname(os.path.abspath(__file__))
if _dashboard_dir not in sys.path:
    sys.path.insert(0, _dashboard_dir)

import streamlit as st
from assets import IMAGES
from themes import get_theme, build_css
from translations import get_t
from utils import load_data
from landing import render_landing

st.set_page_config(
    page_title="AirSentinel Cameroun",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "page" not in st.session_state:
    st.session_state["page"] = "landing"

if "theme_name" not in st.session_state:
    st.session_state["theme_name"] = "dark"

if "lang" not in st.session_state:
    st.session_state["lang"] = "fr"

if st.session_state["page"] == "landing":
    entered = render_landing()
    if entered:
        st.session_state["page"] = "dashboard"
        st.session_state["show_about"] = False
        st.rerun()
    st.stop()

th = get_theme(st.session_state.get("theme_name", "dark"))
T  = get_t(st.session_state.get("lang", "fr"))

# ── Charger les années disponibles dynamiquement ──────────────────────────────
_df_data = load_data()
_an_max  = int(_df_data["date"].dt.year.max())
_an_min  = int(_df_data["date"].dt.year.min())

with st.sidebar:
    # ── Logo ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="position:relative;border-radius:14px;overflow:hidden;
                height:140px;margin-bottom:14px;
                border:1px solid rgba(0,212,177,0.28);
                box-shadow:0 4px 28px rgba(0,212,177,0.14);">
        <img src="{IMAGES['sidebar_top']}"
             style="width:100%;height:100%;object-fit:cover;object-position:center 40%;
                    filter:saturate(0.90) brightness(0.65);"
             onerror="this.style.opacity='0'"/>
        <div style="position:absolute;inset:0;
                    background:{'linear-gradient(135deg,rgba(0,212,177,0.42) 0%,rgba(2,12,24,0.78) 100%)' if th['name']=='dark' else 'linear-gradient(135deg,rgba(0,212,177,0.2) 0%,rgba(212,235,248,0.8) 100%)'};"></div>
        <div style="position:absolute;inset:0;display:flex;flex-direction:column;
                    align-items:center;justify-content:center;text-align:center;padding:10px;">
            <div style="font-size:32px;margin-bottom:4px;">🌍</div>
            <div style="font-size:28px;font-weight:900;color:{th['text']};letter-spacing:-0.03em;text-shadow: 0px 3px 6px rgba(0,0,0,0.5);">AirSentinel</div>
            <div style="font-size:12px;font-weight:800;color:{ th['teal'] if th['name']=='dark' else '#006b58' };letter-spacing:.16em;
                        margin-top:3px;font-family:'DM Mono',monospace;">
                {T['sidebar_app_subtitle']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← " + ("Accueil" if st.session_state["lang"] == "fr" else "Home"),
                 key="btn_home", width='stretch'):
        st.session_state["page"] = "landing"
        st.session_state["show_about"] = False
        st.rerun()

    st.markdown(f"<hr style='border-color:{th['border_soft']};margin:10px 0;'>", unsafe_allow_html=True)

    # ── Paramètres (Thème & Langue) ──────────────────────────────────────────
    st.markdown(
        f"<div style='font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;"
        f"color:{th['text3']};margin-bottom:8px;'>{T['sidebar_theme_title']} & {T['sidebar_lang_title']}</div>",
        unsafe_allow_html=True
    )
    
    col_th, col_lang = st.columns(2)
    th_labels = [T["sidebar_theme_dark"], T["sidebar_theme_light"]]
    th_vals   = ["dark", "light"]
    def update_th_sb():
        st.session_state["theme_name"] = th_vals[th_labels.index(st.session_state.sb_th_sel)]
    with col_th:
        st.selectbox("T", th_labels, index=th_vals.index(st.session_state["theme_name"]), 
                     key="sb_th_sel", on_change=update_th_sb, label_visibility="collapsed")

    l_labels = ["fr Français", "en English"]
    l_vals   = ["fr", "en"]
    def update_lang_sb():
        st.session_state["lang"] = l_vals[l_labels.index(st.session_state.sb_lang_sel)]
        if "tab_radio" in st.session_state:
            del st.session_state["tab_radio"]
    with col_lang:
        st.selectbox("L", l_labels, index=l_vals.index(st.session_state["lang"]), 
                     key="sb_lang_sel", on_change=update_lang_sb, label_visibility="collapsed")

    st.markdown(f"<hr style='border-color:{th['border_soft']};margin:12px 0;'>", unsafe_allow_html=True)

    # ── Profil ────────────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;"
        f"color:{th['text3']};margin-bottom:8px;'>{T['sidebar_profile_title']}</div>",
        unsafe_allow_html=True
    )
    profil_options = [
        T["sidebar_profile_citizen"],
        T["sidebar_profile_health"],
        T["sidebar_profile_mayor"],
        T["sidebar_profile_researcher"],
    ]
    profil = st.selectbox("profil", profil_options, label_visibility="collapsed", key="profil_sel")

    st.markdown(f"<hr style='border-color:{th['border_soft']};margin:12px 0;'>", unsafe_allow_html=True)

    # ── Filtre années ─────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;"
        f"color:{th['text3']};margin-bottom:8px;'>{T['sidebar_period_label']}</div>",
        unsafe_allow_html=True
    )
    st.slider(
        T["sidebar_period_label"],
        _an_min, _an_max, (_an_min, _an_max),
        key="annee_sel",
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    lines = T["sidebar_footer"].split("\n")
    st.markdown(
        f"<div style='font-size:10px;color:{th['text3']};text-align:center;"
        f"line-height:1.9;font-family:DM Mono,monospace;'>"
        f"{lines[0]}<br>{lines[1]}<br>"
        f"<span style='color:{th['teal']};'>{lines[2]}</span></div>",
        unsafe_allow_html=True
    )

# ── CSS global ────────────────────────────────────────────────────────────────
st.markdown(build_css(th, IMAGES["bg_app"]), unsafe_allow_html=True)


# ── Imports des blocs ─────────────────────────────────────────────────────────
from blocs.bloc1_carte       import render as bloc1
from blocs.bloc2_kpis        import render as bloc2
from blocs.bloc3_predictions import render as bloc3
from blocs.bloc4_alertes     import render as bloc4
from blocs.bloc5_decision    import render as bloc5
from blocs.bloc6_shap        import render as bloc6

# ── CSS premium pour les onglets et le bouton À Propos ───────────────────────
st.markdown(f"""
<style>
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px;
    background: {th['bg_tertiary']} !important;
    border-bottom: 1px solid {th['border_soft']};
    padding: 4px 8px 0 8px;
    border-radius: 10px 10px 0 0;
    width: 100% !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
    -webkit-overflow-scrolling: touch !important;
}}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{
    height: 0px !important;
}}

/* Chaque onglet */
.stTabs [data-baseweb="tab"] {{
    font-family: 'Inter', 'DM Sans', sans-serif !important;
    font-size: 13.5px !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: {th['text2']} !important; 
    background: transparent !important;
    border: none !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 10px 10px !important;
    transition: all 0.25s ease !important;
}}

/* Hover */
.stTabs [data-baseweb="tab"]:hover {{
    color: {th['text']} !important;
    background: {th['border_soft']} !important;
}}

/* Onglet actif */
.stTabs [aria-selected="true"] {{
    color: {th['teal'] if th['name']=='dark' else '#006b58'} !important;
    background: {th['border_soft']} !important;
    border-bottom: 3px solid {th['teal']} !important;
    font-weight: 950 !important;
    font-size: 15px !important;
}}

/* Cacher le highlight Streamlit par défaut */
.stTabs [data-baseweb="tab-highlight"] {{
    display: none !important;
}}

/* TRADUCTION SANS RECHARGEMENT DE COMPOSANT STREAMLIT */
.stTabs [data-baseweb="tab"] p {{ display: none !important; }}
.stTabs [data-baseweb="tab"]:nth-child(1)::after {{ content: "{T['tab_carte']}"; display: block; }}
.stTabs [data-baseweb="tab"]:nth-child(2)::after {{ content: "{T['tab_kpis']}"; display: block; }}
.stTabs [data-baseweb="tab"]:nth-child(3)::after {{ content: "{T['tab_predictions']}"; display: block; }}
.stTabs [data-baseweb="tab"]:nth-child(4)::after {{ content: "{T['tab_alertes']}"; display: block; }}
.stTabs [data-baseweb="tab"]:nth-child(5)::after {{ content: "{T['tab_decision']}"; display: block; }}
.stTabs [data-baseweb="tab"]:nth-child(6)::after {{ content: "{T['tab_contexte']}"; display: block; }}
.stTabs [data-baseweb="tab"]:nth-child(7)::after {{ content: "{T['tab_about']}"; display: block; }}
</style>
""", unsafe_allow_html=True)

# ── Barre d'onglets (les rubriques de contenu + À Propos) ───────────────────
tabs = st.tabs(["1", "2", "3", "4", "5", "6", "7"])

# (Ancien JS de restauration supprimé car Streamlit conserve l'état nativement)

with tabs[0]: bloc1(profil)
with tabs[1]: bloc2(profil)
with tabs[2]: bloc3(profil)
with tabs[3]: bloc4(profil)
with tabs[4]: bloc5(profil)
with tabs[5]: bloc6(profil)
with tabs[6]:
    from landing import render_about_inline
    render_about_inline(st.session_state["lang"])

# 7. Modals
if st.session_state.get("show_about", False):
    st.session_state["show_about"] = False
    st.rerun()
