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
from utils import get_img_as_base64

def render_landing():
    # 1. États et Thème
    th_name = st.session_state.get("theme_name", "dark")
    th      = get_theme(th_name)
    lang    = st.session_state.get("lang", "fr")
    T       = get_t(lang)

    # 1.1 Charger le logo personnalisé
    logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.jpg")
    logo_b64  = get_img_as_base64(logo_path)

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

/* Bouton CTA style Premium avec Dégradé */
button[data-testid*="stBaseButton"] {
    background: linear-gradient(135deg, #05f2cb 0%, #00d4b1 100%) !important;
    color: #00302b !important;
    border-radius: 50px !important;
    height: 64px !important;
    padding: 0 60px !important;
    font-size: 26px !important;
    font-weight: 900 !important;
    box-shadow: 0 10px 40px rgba(0, 212, 177, 0.25) !important;
    border: none !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.01em !important;
    text-transform: none !important;
}
button[data-testid*="stBaseButton"]:hover {
    transform: scale(1.05) translateY(-2px) !important;
    box-shadow: 0 15px 50px rgba(0, 212, 177, 0.45) !important;
    filter: brightness(1.1) !important;
}

.brand-title {
    font-size: 52px;
    font-weight: 800;
    letter-spacing: -0.04em;
    font-family: 'Inter', sans-serif;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.brand-air { color: #FFFFFF; }
.brand-sentinel { color: #00d4b1; }

/* Chatbox */
iframe[title="chatbox.render_chatbox"] {
    position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 1000000 !important;
}

/* --- MEDIA QUERIES RESPONSIVE MOBILE --- */
@media (max-width: 768px) {
    .brand-title { font-size: 36px !important; }
    .stApp > header { display: none !important; }
    .slogan-text { font-size: 19px !important; gap: 8px !important; }
    .slogan-text span:nth-child(even) { font-size: 16px !important; }
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) {
        top: 10px !important; right: 10px !important; gap: 4px !important;
    }
    div[data-testid="stSelectbox"] { width: 90px !important; }
    button[data-testid*="stBaseButton"] {
        padding: 0 32px !important; font-size: 22px !important; height: 58px !important;
    }
}

@media (max-width: 480px) {
    .brand-title { font-size: 28px !important; }
    .slogan-text { font-size: 16px !important; flex-direction: column; gap: 4px !important; }
    .slogan-text span:nth-child(even) { display: none !important; }
    .block-container { padding-top: 40px !important; justify-content: flex-start !important; }
    button[data-testid*="stBaseButton"] {
        padding: 0 25px !important; font-size: 19px !important; height: 54px !important;
    }
}
</style>
    """.replace("VAR_BG_URL", bg_url).replace("VAR_OVERLAY", overlay).replace("VAR_TEXT", th['text']).replace("VAR_TEXT2", th['text2'])
    st.markdown(css_code, unsafe_allow_html=True)

    # 3. Logo + AirSentinel + CAMEROUN + séparateur + Slogan
    st.markdown(f"""
    <div style="text-align:center; padding-top: 0; margin-bottom: 10px;">
        <div style="margin-bottom:20px; display:flex; justify-content:center;">
            <img src="data:image/jpeg;base64,{logo_b64}" 
                 style="width:100%; max-width:180px; height:auto; display:block;">
        </div>
        <div class="brand-title">
            <span class="brand-air">Air</span><span class="brand-sentinel">Sentinel</span>
        </div>
        <div style="font-size:13px;color:{'#00d4b1' if th['name']=='dark' else '#00826e'};letter-spacing:0.7em;text-transform:uppercase;font-family:'DM Mono',monospace;font-weight:700;margin-top:8px;">
            {T["landing_subtitle"]}
        </div>
        <div style="display:flex;align-items:center;justify-content:center;gap:20px;margin:20px auto;max-width:320px;width:90%;">
            <div style="flex:1;height:1px;background:linear-gradient(to right,transparent,{'rgba(0,212,177,0.5)' if th['name']=='dark' else 'rgba(0,130,110,0.4)'});"></div>
            <div style="width:7px;height:7px;border-radius:50%;background:{'#00d4b1' if th['name']=='dark' else '#00826e'};"></div>
            <div style="flex:1;height:1px;background:linear-gradient(to left,transparent,{'rgba(0,212,177,0.5)' if th['name']=='dark' else 'rgba(0,130,110,0.4)'});"></div>
        </div>
        <div class="slogan-text" style="font-weight:800;color:{th['text']};font-family:'Inter',sans-serif;margin-bottom:30px;display:flex;align-items:center;justify-content:center;gap:15px;flex-wrap:wrap;font-size:30px;">
            <span>{T["landing_slogan"].split(". ")[0]}</span>
            <span style="color:{'#00d4b1' if th['name']=='dark' else '#00826e'};font-size:26px;">•</span>
            <span>{T["landing_slogan"].split(". ")[1]}</span>
            <span style="color:{'#00d4b1' if th['name']=='dark' else '#00826e'};font-size:26px;">•</span>
            <span>{T["landing_slogan"].split(". ")[2]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Bouton CTA (entre slogan et description)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        enter = st.button(T["landing_btn_enter"], key="enter_dashboard_btn", width='stretch')

    # 5. Description et Footer
    st.markdown(f"""
    <div style="text-align:center; margin-top: 25px; padding: 0 15px;">
        <div style="font-size:16px;color:{th['text2']};line-height:1.6;max-width:580px;margin:0 auto;">
            {T["landing_desc"]}
        </div>
        <div style="margin-top:10px;font-size:11px;color:rgba(248,250,252,0.3);font-family:'DM Mono',monospace;letter-spacing:0.15em;">
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


def get_themed_about_html(th, lang="fr"):
    """
    Lit apropos.html et injecte les variables CSS du thème actuel.
    Encodage des images en base64 inclus.
    """
    about_dir = os.path.join(os.path.dirname(__file__), "about")
    fname = "apropos_en.html" if lang == "en" else "apropos.html"
    html_file = os.path.join(about_dir, fname)
    
    if not os.path.exists(html_file):
        return None

    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Injection dynamique des couleurs depuis le dictionnaire th
    # On remplace les valeurs par défaut définies dans le :root de apropos.html
    replacements = {
        "--bg-primary: #020c18;": f"--bg-primary: {th['bg_primary']};",
        "--bg-secondary: #051525;": f"--bg-secondary: {th['bg_secondary']};",
        "--text-main: #e0f2fe;": f"--text-main: {th['text']};",
        "--text-muted: #7fb8d4;": f"--text-muted: {th['text2']};",
        "--accent-teal: #00d4b1;": f"--accent-teal: {th['teal']};",
        "--border-soft: rgba(0, 212, 177, 0.2);": f"--border-soft: {th.get('border_soft', 'rgba(0,212,177,0.2)')};",
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)

    # Images locales -> Base64
    for img_name in ["about_us.png", "our_mission.png", "air_quality.png", "bsd.png", "fma.png", "fah.png", "prf.png"]:
        img_path = os.path.join(about_dir, img_name)
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode()
            content = content.replace(f'src="{img_name}"', f'src="data:image/png;base64,{b64_data}"')
            
    return content

def render_about_modal(lang):
    """
    Affiche apropos.html dans un dialogue Streamlit avec injection de thème.
    """
    th_name = st.session_state.get("theme_name", "dark")
    th      = get_theme(th_name)
    
    html_content = get_themed_about_html(th, lang)
    if not html_content:
        st.error("Fichier apropos.html introuvable.")
        return

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
    Affiche apropos.html directement (sans modale) avec injection de thème.
    """
    th_name = st.session_state.get("theme_name", "dark")
    th      = get_theme(th_name)
    
    html_content = get_themed_about_html(th, lang)
    if not html_content:
        st.error("Fichier apropos.html introuvable.")
        return
 
    import streamlit.components.v1 as components
    components.html(html_content, height=800, scrolling=True)
