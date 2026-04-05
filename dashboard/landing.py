"""
landing.py — AirSentinel Cameroun
Page d'accueil : Centrage via CSS ciblé sur les éléments Streamlit natifs.
"""
import streamlit as st
from assets import IMAGES
from themes import get_theme
from translations import get_t

def render_landing():
    # 1. États et Thème
    th_name = st.session_state.get("theme_name", "dark")
    th      = get_theme(th_name)
    lang    = st.session_state.get("lang", "fr")
    T       = get_t(lang)

    bg_url  = IMAGES["bg_app"]
    overlay = th["bg_image_overlay"]

    # 2. CSS
    css_code = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap');

section[data-testid="stSidebar"], header[data-testid="stHeader"], footer { display: none !important; }

.stApp {
    background-image: url("VAR_BG_URL");
    background-size: cover;
    background-position: center center;
    background-attachment: fixed;
}
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background: VAR_OVERLAY;
    z-index: 0;
}

/* Conteneur principal centré verticalement et horizontalement */
.block-container {
    max-width: 100% !important;
    min-height: 100vh !important;
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative;
    z-index: 10;
}

/* Tous les éléments directs Streamlit dans le conteneur : centrés */
.block-container > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    width: 100% !important;
}

/* Contrôles Haut Droite */
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) {
    position: fixed !important;
    top: 30px !important;
    right: 40px !important;
    z-index: 10000 !important;
    width: auto !important;
    display: flex !important;
    align-items: center !important;
    gap: 15px !important;
}

/* Stylisation Selectbox & About */
.stSelectbox label { display: none !important; }
div[data-testid="stSelectbox"] { width: 140px !important; }
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #fff !important;
    height: 42px !important;
    font-size: 14px !important;
    border-radius: 12px !important;
}
div[data-testid="column"]:last-child .stButton > button {
    background: rgba(0,212,177,0.85) !important;
    color: #fff !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    height: 44px !important;
    padding: 0 20px !important;
}

/* --- BOUTON CTA : centrage absolu --- */
/* On cible le bouton "enter_dashboard_btn" spécifiquement */
div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stSelectbox"])) {
    justify-content: center !important;
    width: 100% !important;
}
.stButton:has(button[kind="secondary"][key]) {
    display: flex !important;
    justify-content: center !important;
}

/* Bouton CTA style Pill blanc */
button[data-testid="stBaseButton-secondary"] {
    background: #00d4b1 !important;
    color: #003d38 !important;
    border-radius: 50px !important;
    height: 54px !important;
    padding: 0 55px !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2) !important;
    border: none !important;
    transition: all 0.3s ease !important;
    font-family: 'Inter', sans-serif !important;
}
button[data-testid="stBaseButton-secondary"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 15px 45px rgba(0,0,0,0.3) !important;
}

.brand-title {
    font-size: 52px;
    font-weight: 800;
    letter-spacing: -0.04em;
    font-family: 'Inter', sans-serif;
}
.brand-air { color: #f8fafc; }
.brand-sentinel { color: #00d4b1; }

/* Chatbox */
iframe[title="chatbox.render_chatbox"] {
    position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000000 !important;
}
</style>
    """.replace("VAR_BG_URL", bg_url).replace("VAR_OVERLAY", overlay)
    st.markdown(css_code, unsafe_allow_html=True)

    # 3. Logo + AirSentinel + CAMEROUN + séparateur + Slogan
    st.markdown(f"""
    <div style="text-align:center; padding-top: 0; margin-bottom: 10px;">
        <div style="font-size:65px; margin-bottom:12px; filter:drop-shadow(0 15px 35px rgba(0,212,177,0.4));">🌍</div>
        <div class="brand-title">
            <span class="brand-air">Air</span><span class="brand-sentinel">Sentinel</span>
        </div>
        <div style="font-size:13px;color:#00d4b1;letter-spacing:0.7em;text-transform:uppercase;font-family:'DM Mono',monospace;font-weight:700;margin-top:8px;">
            CAMEROUN
        </div>
        <div style="display:flex;align-items:center;justify-content:center;gap:20px;margin:20px auto;width:320px;">
            <div style="flex:1;height:1px;background:linear-gradient(to right,transparent,rgba(0,212,177,0.5));"></div>
            <div style="width:7px;height:7px;border-radius:50%;background:#00d4b1;"></div>
            <div style="flex:1;height:1px;background:linear-gradient(to left,transparent,rgba(0,212,177,0.5));"></div>
        </div>
        <div style="font-size:30px;font-weight:800;color:#f8fafc;font-family:'Inter',sans-serif;margin-bottom:30px;display:flex;align-items:center;justify-content:center;gap:15px;flex-wrap:wrap;">
            <span>Anticiper</span>
            <span style="color:#00d4b1;font-size:26px;">•</span>
            <span>Alerter</span>
            <span style="color:#00d4b1;font-size:26px;">•</span>
            <span>Protéger</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Bouton CTA (entre slogan et description)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        enter = st.button(T["landing_btn_enter"], key="enter_dashboard_btn", use_container_width=True)

    # 5. Description et Footer
    st.markdown(f"""
    <div style="text-align:center; margin-top: 25px;">
        <div style="font-size:16px;color:rgba(248,250,252,0.8);line-height:1.6;max-width:580px;margin:0 auto;">
            {T["landing_desc"]}
        </div>
        <div style="margin-top:25px;font-size:11px;color:rgba(248,250,252,0.3);font-family:'DM Mono',monospace;letter-spacing:0.15em;">
            {T["sidebar_footer"].splitlines()[0]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. Contrôles Haut Droite
    cols = st.columns([1, 1, 1])
    with cols[0]:
        th_labels = [T["sidebar_theme_dark"], T["sidebar_theme_light"]]
        th_vals   = ["dark", "light"]
        cur_th_idx = th_vals.index(th_name)
        th_choice = st.selectbox("T", th_labels, index=cur_th_idx, key="sel_th_top", label_visibility="collapsed")
        if th_vals[th_labels.index(th_choice)] != th_name:
            st.session_state["theme_name"] = th_vals[th_labels.index(th_choice)]
            st.rerun()
    with cols[1]:
        l_labels = ["fr Français", "us English"]
        l_vals   = ["fr", "en"]
        cur_l_idx = l_vals.index(lang)
        l_choice = st.selectbox("L", l_labels, index=cur_l_idx, key="sel_lang_top", label_visibility="collapsed")
        if l_vals[l_labels.index(l_choice)] != lang:
            st.session_state["lang"] = l_vals[l_labels.index(l_choice)]
            st.rerun()
    with cols[2]:
        about_label = "ℹ️ À Propos" if lang == "fr" else "ℹ️ About"
        if st.button(about_label, key="btn_about_top"):
            st.session_state["show_about"] = True

    if st.session_state.get("show_about", False):
        from landing import render_about_modal
        render_about_modal(lang)

    return enter


def render_about_modal(lang):
    title = "L'ÉQUIPE DPA GREEN TECH" if lang == "fr" else "THE DPA GREEN TECH TEAM"
    close_btn = "OK"
    team = [
        {"name": "BODEHOU Sabine", "school": "ISSEA", "role": "Data Science", "img": "https://images.unsplash.com/photo-1573496359142-b8d87734a7a2?w=400&h=400&fit=crop"},
        {"name": "FANKAM Marc Aurel", "school": "ISSEA", "role": "Modélisation", "img": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&h=400&fit=crop"},
        {"name": "PEURBAR RIMBAR Firmin", "school": "ISSEA", "role": "SHAP & Rapport", "img": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop"},
        {"name": "FOFACK ALEMDJOU Henri Joël", "school": "ENSP", "role": "Frontend & API", "img": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=400&fit=crop"}
    ]
    @st.dialog("À Propos" if lang == "fr" else "About", width="large")
    def show_dialog():
        st.markdown(f'<div style="text-align:center;margin-bottom:22px;"><h2 style="color:#00d4b1;">{title}</h2></div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for i, m in enumerate(team):
            with cols[i]:
                st.markdown(f"""
                <div style="text-align:center;background:rgba(255,255,255,0.03);padding:18px;border-radius:18px;border:1px solid rgba(0,212,177,0.12);">
                    <img src="{m['img']}" style="width:100%;border-radius:50%;margin-bottom:12px;border:2px solid #00d4b1;">
                    <div style="font-weight:700;color:#e0f2fe;font-size:15px;margin-bottom:4px;">{m['name']}</div>
                    <div style="font-size:12px;color:#00d4b1;font-weight:600;margin-bottom:4px;">{m['school']}</div>
                    <div style="font-size:11px;color:rgba(224,242,254,0.5);line-height:1.4;">{m['role']}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        if st.button(close_btn, use_container_width=True, key="about_ok_btn"):
            st.session_state["show_about"] = False
            st.rerun()
    show_dialog()
