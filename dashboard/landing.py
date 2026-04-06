"""
landing.py — AirSentinel Cameroun
Page d'accueil : Centrage via CSS ciblé sur les éléments Streamlit natifs.
"""
import streamlit as st
import base64
import os
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
    top: 20px !important;
    right: 25px !important;
    z-index: 10000 !important;
    width: auto !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
}

/* Stylisation Selectbox & About */
.stSelectbox label { display: none !important; }
div[data-testid="stSelectbox"] { width: 110px !important; }
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #fff !important;
    height: 36px !important;
    font-size: 12.5px !important;
    border-radius: 10px !important;
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
.brand-air { color: VAR_TEXT; }
.brand-sentinel { color: #00d4b1; }

/* Chatbox */
iframe[title="chatbox.render_chatbox"] {
    position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000000 !important;
}
</style>
    """.replace("VAR_BG_URL", bg_url).replace("VAR_OVERLAY", overlay).replace("VAR_TEXT", th['text']).replace("VAR_TEXT2", th['text2'])
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
        <div style="font-size:30px;font-weight:800;color:{th['text']};font-family:'Inter',sans-serif;margin-bottom:30px;display:flex;align-items:center;justify-content:center;gap:15px;flex-wrap:wrap;">
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
        enter = st.button(T["landing_btn_enter"], key="enter_dashboard_btn", width='stretch')

    # 5. Description et Footer
    st.markdown(f"""
    <div style="text-align:center; margin-top: 25px;">
        <div style="font-size:16px;color:{th['text2']};line-height:1.6;max-width:580px;margin:0 auto;">
            {T["landing_desc"]}
        </div>
        <div style="margin-top:25px;font-size:11px;color:rgba(248,250,252,0.3);font-family:'DM Mono',monospace;letter-spacing:0.15em;">
            {T["sidebar_footer"].splitlines()[0]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. Contrôles Haut Droite
    cols = st.columns([1, 1])
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

    return enter


def render_about_modal(lang):
    """
    Lit le fichier apropos.html et l'affiche dans un dialogue Streamlit.
    Les images locales sont encodées en base64 pour s'afficher proprement.
    """
    about_dir = os.path.join(os.path.dirname(__file__), "about")
    html_file = os.path.join(about_dir, "apropos.html")
    
    if not os.path.exists(html_file):
        st.error("Fichier apropos.html introuvable dans dashboard/about/")
        return

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Routine d'encodage des images en base64
    for img_name in ["bsd.png", "fma.png", "fah.png", "prf.png"]:
        img_path = os.path.join(about_dir, img_name)
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode()
            html_content = html_content.replace(f'src="{img_name}"', f'src="data:image/png;base64,{b64_data}"')

    @st.dialog("À Propos" if lang == "fr" else "About", width="large")
    def show_dialog():
        # On injecte le style harmonisé pour le bouton de fermeture
        st.markdown("""
        <style>
        div[data-testid="stDialog"] .stButton > button {
            background: #00d4b1 !important;
            color: #003d38 !important;
            border-radius: 50px !important;
            height: 48px !important;
            padding: 0 40px !important;
            font-size: 16px !important;
            font-weight: 800 !important;
            box-shadow: 0 10px 40px rgba(0,212,177,0.15) !important;
            border: none !important;
            transition: all 0.3s ease !important;
            font-family: 'Inter', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            margin-top: 15px !important;
        }
        div[data-testid="stDialog"] .stButton > button:hover {
            transform: translateY(-2px) !important;
            background: #05f2cb !important;
            box-shadow: 0 15px 45px rgba(0,212,177,0.25) !important;
        }
        /* Ajustement de la zone du dialogue pour le HTML */
        div[data-testid="stDialog"] [data-testid="stVerticalBlock"] > div:first-child {
            padding: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Affichage du contenu HTML via un composant Streamlit
        import streamlit.components.v1 as components
        components.html(html_content, height=680, scrolling=True)
        
        # Bouton stylisé pour fermer et revenir au dashboard
        close_txt = "RETOURNER AU DASHBOARD ✅" if lang == "fr" else "BACK TO DASHBOARD ✅"
        if st.button(close_txt, width='stretch', key="about_ok_btn"):
            st.session_state["show_about"] = False
            st.rerun()
    show_dialog()

def render_about_inline(lang):
    """
    Lit le fichier apropos.html et l'affiche directement dans un composant (sans modale).
    """
    about_dir = os.path.join(os.path.dirname(__file__), "about")
    html_file = os.path.join(about_dir, "apropos.html")
    
    if not os.path.exists(html_file):
        st.error("Fichier apropos.html introuvable dans dashboard/about/")
        return

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    for img_name in ["bsd.png", "fma.png", "fah.png", "prf.png"]:
        img_path = os.path.join(about_dir, img_name)
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode()
            html_content = html_content.replace(f'src="{img_name}"', f'src="data:image/png;base64,{b64_data}"')

    import streamlit.components.v1 as components
    components.html(html_content, height=800, scrolling=True)
