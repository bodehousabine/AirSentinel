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
from utils import get_context, banner, irs_level, VILLES, REGIONS
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

if st.session_state["page"] == "landing":
    entered = render_landing()
    if entered:
        st.session_state["page"] = "dashboard"
        st.rerun()
    st.stop()

_th = get_theme(st.session_state.get("theme_name", "dark"))
_T  = get_t(st.session_state.get("lang", "fr"))

with st.sidebar:
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
                 key="btn_home", width="stretch"):
        st.session_state["page"] = "landing"
        st.rerun()

    st.markdown(f"<hr style='border-color:{_th['border_soft']};margin:10px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <style>
    div[data-testid="stSidebar"] .theme-lang-block label { color: #0a1f33 !important; font-weight: 600 !important; font-size: 11px !important; }
    div[data-testid="stSidebar"] .theme-lang-block [data-baseweb="select"] > div { background: rgba(255,255,255,0.95) !important; border: 1px solid rgba(0,130,110,0.40) !important; border-radius: 8px !important; color: #0a1f33 !important; }
    div[data-testid="stSidebar"] .theme-lang-block [data-baseweb="select"] span { color: #0a1f33 !important; font-weight: 500 !important; }
    </style>
    <div class="theme-lang-block">
    """, unsafe_allow_html=True)

    col_th, col_lang = st.columns(2)
    with col_th:
        theme_labels = [_T["sidebar_theme_dark"], _T["sidebar_theme_light"]]
        theme_vals   = ["dark", "light"]
        cur_idx = theme_vals.index(st.session_state.get("theme_name", "dark"))
        choice_th = st.selectbox(_T["sidebar_theme_label"], theme_labels, index=cur_idx, key="_theme_choice")
        st.session_state["theme_name"] = theme_vals[theme_labels.index(choice_th)]

    with col_lang:
        lang_labels = ["Français", "English"]
        lang_vals   = ["fr", "en"]
        cur_lidx = lang_vals.index(st.session_state.get("lang", "fr"))
        choice_lang = st.selectbox(_T["sidebar_lang_label"], lang_labels, index=cur_lidx, key="_lang_choice")
        st.session_state["lang"] = lang_vals[lang_labels.index(choice_lang)]

    st.markdown('</div>', unsafe_allow_html=True)

    th = get_theme(st.session_state["theme_name"])
    T  = get_t(st.session_state["lang"])

    st.markdown(f"<hr style='border-color:{th['border_soft']};margin:12px 0;'>", unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:{th['text3']};margin-bottom:8px;'>{T['sidebar_profile_title']}</div>", unsafe_allow_html=True)
    profil_options = [T["sidebar_profile_citizen"], T["sidebar_profile_health"], T["sidebar_profile_mayor"], T["sidebar_profile_researcher"]]
    profil = st.selectbox("profil", profil_options, label_visibility="collapsed", key="profil_sel")

    st.markdown(f"<hr style='border-color:{th['border_soft']};margin:12px 0;'>", unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:{th['text3']};margin-bottom:10px;'>{T['sidebar_filters_title']}</div>", unsafe_allow_html=True)

    all_city   = T["sidebar_city_all"]
    all_region = T["sidebar_region_all"]

    ville_choices = st.multiselect(T["sidebar_city_label"], options=[all_city] + sorted(VILLES), default=[all_city], key="ville_multi")
    st.session_state["ville_sel_list"] = "ALL" if (all_city in ville_choices or len(ville_choices) == 0) else ville_choices

    region_choices = st.multiselect(T["sidebar_region_label"], options=[all_region] + sorted(REGIONS), default=[all_region], key="region_multi")
    st.session_state["region_sel_list"] = "ALL" if (all_region in region_choices or len(region_choices) == 0) else region_choices

    st.slider(T["sidebar_period_label"], 2022, 2025, (2022, 2025), key="annee_sel")

    filtres = []
    vs = st.session_state.get("ville_sel_list", "ALL")
    rs = st.session_state.get("region_sel_list", "ALL")
    a  = st.session_state.get("annee_sel", (2022, 2025))
    if vs != "ALL" and isinstance(vs, list): filtres += vs
    if rs != "ALL" and isinstance(rs, list): filtres += rs
    if a  != (2022, 2025): filtres.append(f"{a[0]}–{a[1]}")

    if filtres:
        st.markdown(f"""<div style="background:rgba(0,212,177,0.10);border:1px solid rgba(0,212,177,0.26);border-radius:10px;padding:10px 13px;margin-top:10px;"><div style="font-size:10px;color:{th['teal']};margin-bottom:4px;letter-spacing:.08em;text-transform:uppercase;">{T['sidebar_active_filters']}</div><div style="font-size:12px;color:{th['text']};line-height:1.7;">{"  ·  ".join(filtres)}</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="font-size:11px;color:{th['text3']};margin-top:10px;text-align:center;padding:8px;border-radius:8px;border:1px solid {th['border_soft']};background:{'rgba(14,165,233,0.05)' if th['name']=='dark' else 'rgba(10,60,120,0.05)'};">{T['sidebar_no_filter']}</div>""", unsafe_allow_html=True)

    st.markdown(f"<hr style='border-color:{th['border_soft']};margin:12px 0;'>", unsafe_allow_html=True)
    lines = T["sidebar_footer"].split("\n")
    st.markdown(f"""<div style="font-size:10px;color:{th['text3']};text-align:center;line-height:1.9;font-family:'DM Mono',monospace;">{lines[0]}<br>{lines[1]}<br><span style="color:{th['teal']};">{lines[2]}</span></div>""", unsafe_allow_html=True)

st.markdown(build_css(th, IMAGES["bg_app"]), unsafe_allow_html=True)

banner(img_url=IMAGES["header_banner"], height=235, title=T["header_title"], subtitle=T["header_subtitle"], th=th, accent=th["teal"], tint_hex="#00d4b1", tint_strength=0.30)

ctx = get_context()
nc, nt, _ = irs_level(ctx["irs_moy"], ctx["p50"], ctx["p75"], ctx["p90"], T, th)

pills = [
    (T["header_pill_profile"], profil,                                    th["purple"]),
    (T["header_pill_pm25"],    f"{ctx['pm25_moy']:.1f} µg/m³",            th["red"] if ctx["pm25_moy"]>15 else th["green"]),
    (T["header_pill_irs"],     f"{nt} ({ctx['irs_moy']:.3f})",            nc),
    (T["header_pill_scope"],   ctx["scope_label"],                         th["blue"]),
    (T["header_pill_source"],  "WHO AQG 2021 · NCBI NBK574591",            th["text3"]),
]
pills_html = "".join([f'<div style="font-size:11px;background:linear-gradient(135deg,{th["bg_tertiary"]},{th["bg_elevated"]});border:1px solid {th["border_soft"]};padding:5px 14px;border-radius:20px;display:flex;align-items:center;gap:6px;"><span style="color:{th["text3"]}">{lbl} :</span><span style="color:{vc};font-weight:500;">{val}</span></div>' for lbl, val, vc in pills])
st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px;">{pills_html}</div>', unsafe_allow_html=True)

# ── ONGLETS ───────────────────────────────────────────────────────────────────
from blocs.bloc1_carte       import render as bloc1
from blocs.bloc2_kpis        import render as bloc2
from blocs.bloc3_predictions import render as bloc3
from blocs.bloc4_alertes     import render as bloc4
from blocs.bloc5_decision    import render as bloc5
from blocs.bloc6_contexte    import render as bloc6

tabs = st.tabs([T["tab_carte"], T["tab_kpis"], T["tab_predictions"], T["tab_alertes"], T["tab_decision"], T["tab_contexte"]])

with tabs[0]: bloc1(profil)
with tabs[1]: bloc2(profil)
with tabs[2]: bloc3(profil)
with tabs[3]: bloc4(profil)
with tabs[4]: bloc5(profil)
with tabs[5]: bloc6(profil)

render_chatbox()
