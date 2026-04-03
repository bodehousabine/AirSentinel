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
from utils import get_context, banner, irs_level, load_data
from landing import render_landing
from chatbox import render_chatbox

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
        st.rerun()
    st.stop()

_th = get_theme(st.session_state.get("theme_name", "dark"))
_T  = get_t(st.session_state.get("lang", "fr"))

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
                    background:linear-gradient(135deg,rgba(0,212,177,0.42) 0%,rgba(2,12,24,0.78) 100%);"></div>
        <div style="position:absolute;inset:0;display:flex;flex-direction:column;
                    align-items:center;justify-content:center;text-align:center;padding:10px;">
            <div style="font-size:32px;margin-bottom:4px;">🌍</div>
            <div style="font-size:17px;font-weight:600;color:#e0f2fe;">AirSentinel</div>
            <div style="font-size:10px;color:#00d4b1;letter-spacing:.16em;
                        margin-top:3px;font-family:'DM Mono',monospace;">
                {_T['sidebar_app_subtitle']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← " + ("Accueil" if _T == get_t("fr") else "Home"),
                 key="btn_home", use_container_width=True):
        st.session_state["page"] = "landing"
        st.rerun()

    st.markdown(f"<hr style='border-color:{_th['border_soft']};margin:10px 0;'>", unsafe_allow_html=True)

    # ── Thème + Langue ────────────────────────────────────────────────────────
    col_th, col_lang = st.columns(2)
    with col_th:
        theme_labels = [_T["sidebar_theme_dark"], _T["sidebar_theme_light"]]
        theme_vals   = ["dark", "light"]
        cur_idx      = theme_vals.index(st.session_state.get("theme_name", "dark"))
        choice_th    = st.selectbox(_T["sidebar_theme_label"], theme_labels, index=cur_idx, key="_theme_choice")
        st.session_state["theme_name"] = theme_vals[theme_labels.index(choice_th)]

    with col_lang:
        lang_labels = ["Français", "English"]
        lang_vals   = ["fr", "en"]
        cur_lidx    = lang_vals.index(st.session_state.get("lang", "fr"))
        choice_lang = st.selectbox(_T["sidebar_lang_label"], lang_labels, index=cur_lidx, key="_lang_choice")
        st.session_state["lang"] = lang_vals[lang_labels.index(choice_lang)]

    th = get_theme(st.session_state["theme_name"])
    T  = get_t(st.session_state["lang"])

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

    # ── Filtre années — utilisé par KPIs uniquement ───────────────────────────
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

# ── Bannière principale ───────────────────────────────────────────────────────

ctx = get_context()
nc, nt, _ = irs_level(ctx["irs_moy"], ctx["p50"], ctx["p75"], ctx["p90"], T, th)

pills = [
    (T["header_pill_profile"], profil,                                 th["purple"]),
    (T["header_pill_pm25"],    f"{ctx['pm25_moy']:.1f} µg/m³",         th["red"] if ctx["pm25_moy"] > 15 else th["green"]),
    (T["header_pill_irs"],     f"{nt} ({ctx['irs_moy']:.3f})",         nc),
    (T["header_pill_scope"],   ctx["scope_label"],                      th["blue"]),
    (T["header_pill_source"],  "WHO AQG 2021 · NCBI NBK574591",         th["text3"]),
]
pills_html = "".join([
    f'<div style="font-size:11px;background:linear-gradient(135deg,{th["bg_tertiary"]},{th["bg_elevated"]});'
    f'border:1px solid {th["border_soft"]};padding:5px 14px;border-radius:20px;'
    f'display:flex;align-items:center;gap:6px;">'
    f'<span style="color:{th["text3"]}">{lbl} :</span>'
    f'<span style="color:{vc};font-weight:500;">{val}</span></div>'
    for lbl, val, vc in pills
])
st.markdown(
    f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px;">{pills_html}</div>',
    unsafe_allow_html=True
)

# ── Onglets ───────────────────────────────────────────────────────────────────
from blocs.bloc1_carte       import render as bloc1
from blocs.bloc2_kpis        import render as bloc2
from blocs.bloc3_predictions import render as bloc3
from blocs.bloc4_alertes     import render as bloc4
from blocs.bloc5_decision    import render as bloc5
from blocs.bloc6_shap        import render as bloc6

tabs = st.tabs([
    T["tab_carte"], T["tab_kpis"], T["tab_predictions"],
    T["tab_alertes"], T["tab_decision"], T["tab_contexte"]
])

with tabs[0]: bloc1(profil)
with tabs[1]: bloc2(profil)
with tabs[2]: bloc3(profil)
with tabs[3]: bloc4(profil)
with tabs[4]: bloc5(profil)
with tabs[5]: bloc6(profil)

render_chatbox()
