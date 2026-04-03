"""
landing.py — AirSentinel Cameroun
Page d'accueil : fond ville Yaoundé, structure centrée originale.
Contrôles (Thème, Langue, À Propos) alignés en haut à droite.
"""
import streamlit as st
from assets import IMAGES
from themes import get_theme
from translations import get_t
from chatbox import render_chatbox


def render_landing():
    # 1. State and Theme
    th_name = st.session_state.get("theme_name", "dark")
    th      = get_theme(th_name)
    lang    = st.session_state.get("lang", "fr")
    T       = get_t(lang)
    
    # Render chatbox early so it's not pushed off-screen
    render_chatbox()

    bg_url  = IMAGES["bg_app"]
    overlay = th["bg_image_overlay"]
    text_color = th["text"]
    text2_color = th["text2"]

    # 2. Premium CSS for Layout and Glassmorphism
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap');

.block-container {{
    position: relative; z-index: 10;
    padding-top: 0 !important;
    margin-top: 0 !important;
    max-width: 100% !important;
    height: 100vh !important;
overflow: hidden !important;
}}
.stApp {{
    background-image: url("{bg_url}");
    background-size: cover;
    background-position: center center;
    background-attachment: fixed;
    overflow: hidden !important;
}}
.stApp::before {{
    content: '';
    position: fixed; inset: 0;
    background: {overlay};
    z-index: 0;
}}
section[data-testid="stSidebar"], header[data-testid="stHeader"], footer {{ display: none !important; }}

/* --- Top-Right Controls Positioning --- */
div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) {{
position: fixed !important;
top: 30px !important;
right: 40px !important;
z-index: 10000 !important;
width: auto !important;
display: flex !important;
align-items: center !important;
gap: 15px !important;
}}

/* Individual Box Styling */
div[data-testid="column"] {{
width: auto !important;
min-width: unset !important;
flex: unset !important;
}}

.stSelectbox, .stButton {{
background: rgba(255, 255, 255, 0.04) !important;
backdrop-filter: blur(15px) !important;
-webkit-backdrop-filter: blur(15px) !important;
border: 1px solid rgba(255, 255, 255, 0.1) !important;
border-radius: 12px !important;
transition: all 0.3s ease !important;
}}

.stSelectbox:hover, .stButton:hover {{
background: rgba(255, 255, 255, 0.08) !important;
border-color: rgba(0, 212, 177, 0.4) !important;
}}

/* Selectbox specific */
div[data-testid="stSelectbox"] {{
width: 140px !important;
}}
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
background: transparent !important;
border: none !important;
color: #fff !important;
height: 42px !important;
font-size: 14px !important;
}}

/* About Button Box (Solid Teal) */
div[data-testid="column"]:last-child .stButton > button {{
background: #00d4b1 !important;
color: #fff !important;
border: none !important;
border-radius: 10px !important;
height: 44px !important;
padding: 0 20px !important;
font-weight: 600 !important;
font-size: 14px !important;
box-shadow: 0 4px 15px rgba(0, 212, 177, 0.3) !important;
}}

/* Hero Section - Absolute Center Force */
.hero-container {{
position: fixed !important;
top: 42% !important;
left: 50% !important;
transform: translate(-50%, -50%) !important;
z-index: 1000 !important;
display: flex !important;
flex-direction: column !important;
align-items: center !important;
justify-content: center !important;
text-align: center !important;
width: 90% !important;
max-width: 800px !important;
margin-top: 0 !important;
}}

/* Brand Name */
.brand-title {{
font-size: 38px;
font-weight: 800;
letter-spacing: -0.04em;
margin-bottom: 0px;
line-height: 1.1;
font-family: 'Inter', sans-serif;
}}

/* Dashboard Button - Forced Position */
div[data-testid="stColumn"] {{
    display: flex !important;
    justify-content: center !important;
}}

#enter_dashboard_container {{
    margin-top: 10px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}}

#enter_dashboard_container .stButton > button {{
    width: 280px !important;
}}
.brand-air {{ color: #f8fafc; }}
.brand-sentinel {{ color: #00d4b1; }}

/* Access Button - White Pill (Reduced size for One Page) */
[data-testid="stColumn"] .stButton > button {{
background: #ffffff !important;
color: #000 !important;
border: none !important;
border-radius: 50px !important;
height: 48px !important;
width: 100% !important;
padding: 0 45px !important;
font-size: 16px !important;
font-weight: 700 !important;
box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
font-family: 'Inter', sans-serif !important;
}}
[data-testid="stColumn"] .stButton > button:hover {{
transform: translateY(-2px) !important;
box-shadow: 0 12px 35px rgba(0,0,0,0.2) !important;
}}

    .stSelectbox label {{ display: none !important; }}
    
    /* Global fix for Chatbox Iframe Positioning */
    iframe[title="chatbox.render_chatbox"] {{
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 1000000 !important;
    }}
    
    </style>
""", unsafe_allow_html=True)

    # 3. Hero Content (Absolute Centering)
    hero_html = f"""
<div class="hero-container">
<div style="font-size:50px;margin-bottom:10px;filter:drop-shadow(0 15px 35px rgba(0,212,177,0.4));">🌍</div>
<div class="brand-title">
<span class="brand-air">Air</span><span class="brand-sentinel">Sentinel</span>
</div>
<div style="margin-bottom:5px;">
<span style="font-size:12px;color:rgba(0,212,177,0.9);letter-spacing:0.6em;text-transform:uppercase;font-family:'DM Mono',monospace;font-weight:600;">
CAMEROUN
</span>
</div>
<div style="display:flex;align-items:center;justify-content:center;gap:15px;margin-bottom:10px;width:100%;max-width:300px;margin:0 auto;">
<div style="flex:1;height:1px;background:linear-gradient(to right,transparent,rgba(0,212,177,0.5));"></div>
<div style="width:6px;height:6px;border-radius:50%;background:#00d4b1;"></div>
<div style="flex:1;height:1px;background:linear-gradient(to left,transparent,rgba(0,212,177,0.5));"></div>
</div>
<div style="margin-bottom:10px;">
<div style="font-size:24px;font-weight:800;color:#f8fafc;font-family:'Inter',sans-serif;">{T["landing_slogan"]}</div>
</div>
<div style="margin-bottom:20px;">
<div style="font-size:15px;color:rgba(248,250,252,0.8);line-height:1.4;max-width:550px;margin:0 auto;">{T["landing_desc"]}</div>
</div>
<div style="margin-top: 15px; font-size:10px;color:rgba(248,250,252,0.4);font-family:'DM Mono',monospace;">
{T["sidebar_footer"].splitlines()[0]}
</div>
</div>
""".strip()
    st.markdown(hero_html, unsafe_allow_html=True)

    # 4. Entry Button (Centered independently in fixed position)
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        # We wrap it in a container that we will target with CSS
        st.markdown('<div id="enter_dashboard_container">', unsafe_allow_html=True)
        enter = st.button(T["landing_btn_enter"], key="enter_dashboard_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. Top-Right Controls (Fixed in corner)
    cols = st.columns([1, 1, 1])
    with cols[0]:
        th_labels = [T["sidebar_theme_dark"], T["sidebar_theme_light"]]
        th_vals   = ["dark", "light"]
        cur_th_idx = th_vals.index(th_name)
        th_choice = st.selectbox("T", th_labels, index=cur_th_idx, key="sel_th_top", label_visibility="collapsed")
        new_th = th_vals[th_labels.index(th_choice)]
        if new_th != th_name:
            st.session_state["theme_name"] = new_th
            st.rerun()

    with cols[1]:
        l_labels = ["fr Français", "us English"]
        l_vals   = ["fr", "en"]
        cur_l_idx = l_vals.index(lang)
        l_choice = st.selectbox("L", l_labels, index=cur_l_idx, key="sel_lang_top", label_visibility="collapsed")
        new_lang = l_vals[l_labels.index(l_choice)]
        if new_lang != lang:
            st.session_state["lang"] = new_lang
            st.rerun()
    
    with cols[2]:
        about_label = "ℹ️ À Propos" if lang == "fr" else "ℹ️ About"
        if st.button(about_label, key="btn_about_top"):
            st.session_state["show_about"] = True

    # 6. Modal Presentation
    if st.session_state.get("show_about", False):
        render_about_modal(lang)
    
    return enter


def render_about_modal(lang):
    title = "L'ÉQUIPE DPA GREEN TECH" if lang == "fr" else "THE DPA GREEN TECH TEAM"
    close_btn = "OK"

    team = [
        {
            "name": "BODEHOU Sabine",
            "school": "ISSEA",
            "role": "Data Science",
            "img": "https://images.unsplash.com/photo-1573496359142-b8d87734a7a2?w=400&h=400&fit=crop"
        },
        {
            "name": "FANKAM Marc Aurel",
            "school": "ISSEA",
            "role": "Modélisation",
            "img": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&h=400&fit=crop"
        },
        {
            "name": "PEURBAR RIMBAR Firmin",
            "school": "ISSEA",
            "role": "SHAP & Rapport",
            "img": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop"
        },
        {
            "name": "FOFACK ALEMDJOU Henri Joël",
            "school": "ENSP",
            "role": "Frontend & API",
            "img": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=400&fit=crop"
        }
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
