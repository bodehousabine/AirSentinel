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
            <div style="font-size:17px;font-weight:600;color:{th['text']};">AirSentinel</div>
            <div style="font-size:10px;color:{ th['teal'] if th['name']=='dark' else '#006b58' };letter-spacing:.16em;
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
        f"<div style='font-size:10px;text-transform:uppercase;letter-spacing:.1em;"
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
        f"<div style='font-size:10px;text-transform:uppercase;letter-spacing:.1em;"
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
        f"<div style='font-size:10px;text-transform:uppercase;letter-spacing:.1em;"
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
    about_label = "ℹ️ À Propos" if st.session_state["lang"] == "fr" else "ℹ️ About"
    if st.button(about_label, key="sb_about_btn", width='stretch'):
        st.session_state["show_about"] = True

    st.markdown(f"<hr style='border-color:{th['border_soft']};margin:12px 0;'>", unsafe_allow_html=True)

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

# ── CSS premium pour les onglets ───────────────────────────────────────────────
st.markdown(f"""
<style>
/* Conteneur des onglets — fond dynamique selon thème */
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px;
    background: {th['bg_tertiary']} !important;
    border-bottom: 1px solid {th['border_soft']};
    padding: 4px 8px 0 8px;
    border-radius: 10px 10px 0 0;
}}

/* Chaque onglet */
.stTabs [data-baseweb="tab"] {{
    font-family: 'Inter', 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 950 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: {th['text2']} !important; 
    background: transparent !important;
    border: none !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 12px 22px !important;
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
    font-size: 16px !important;
}}

/* Cacher le highlight Streamlit par défaut */
.stTabs [data-baseweb="tab-highlight"] {{
    display: none !important;
}}

/* ── Spécifique Sidebar : Boutons Accueil & Apropos ── */
section[data-testid="stSidebar"] .stButton > button {{
    background: {th['bg_tertiary']} !important;
    color: {th['text']} !important;
    border: 1px solid {th['border_soft']} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    border-color: {th['teal']} !important;
    background: {th['border_soft']} !important;
    color: {th['teal'] if th['name']=='dark' else '#006b58'} !important;
}}
</style>
""", unsafe_allow_html=True)


tabs = st.tabs([
    T["tab_carte"], T["tab_kpis"], T["tab_predictions"],
    T["tab_alertes"], T["tab_decision"], T["tab_contexte"]
])

# Capture the currently active tab from localStorage if it exists, and click it
# We use standard JS to detect clicks on tabs and save their index.
import time
js_restore_tab = f"""
<script>
    // {time.time()} 
    const tabs = window.parent.document.querySelectorAll('.stTabs [data-baseweb="tab"]');
    if (tabs.length > 0) {{
        tabs.forEach((tab, index) => {{
            tab.addEventListener('click', () => {{
                window.parent.sessionStorage.setItem('air_active_tab', index);
            }});
        }});
        const savedTab = window.parent.sessionStorage.getItem('air_active_tab');
        if (savedTab !== null && tabs[savedTab]) {{
            if (tabs[savedTab].getAttribute('aria-selected') !== 'true') {{
                tabs[savedTab].click();
            }}
        }}
    }}
</script>
"""
import streamlit.components.v1 as components
components.html(js_restore_tab, height=0, width=0)

with tabs[0]: bloc1(profil)
with tabs[1]: bloc2(profil)
with tabs[2]: bloc3(profil)
with tabs[3]: bloc4(profil)
with tabs[4]: bloc5(profil)
with tabs[5]: bloc6(profil)

# 7. Modals
if st.session_state.get("show_about", False):
    from landing import render_about_modal
    render_about_modal(st.session_state["lang"])
