"""
themes.py — AirSentinel Cameroun
Deux thèmes complets : sombre (bleu de mer) et clair (bleu ciel).
Usage : TH = get_theme(theme_name)
"""

THEMES = {

    # ══════════════════════════════════════════════════════════════════════════
    # THÈME SOMBRE — bleu de mer profond (thème original)
    # ══════════════════════════════════════════════════════════════════════════
    "dark": {
        # Fonds
        "bg_primary":   "#020c18",
        "bg_secondary": "#051525",
        "bg_tertiary":  "#071e35",
        "bg_elevated":  "#0a2845",
        "bg_card":      "#0d2f50",
        # Textes
        "text":         "#e0f2fe",
        "text2":        "#7fb8d4",
        "text3":        "#3d6b8a",
        # Bordures
        "border_soft":  "rgba(14,165,233,0.14)",
        "border_med":   "rgba(14,165,233,0.28)",
        "border_teal":  "rgba(0,212,177,0.22)",
        # Plotly
        "plot_bg":      "rgba(7,30,53,0.85)",
        "grid_color":   "rgba(56,189,248,0.09)",
        "line_color":   "rgba(56,189,248,0.16)",
        # Sidebar
        "sidebar_bg":   "linear-gradient(180deg,#020c18 0%,#051525 100%)",
        # Image fond
        "bg_image_overlay": "linear-gradient(145deg,rgba(2,12,24,0.88) 0%,rgba(3,17,31,0.82) 40%,rgba(5,25,41,0.80) 100%)",
        # CSS Streamlit overrides
        "streamlit_bg": "#020c18",
        "streamlit_secondary_bg": "#071e35",
        "streamlit_text": "#e0f2fe",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # THÈME CLAIR — bleu ciel lumineux (lisibilité maximale garantie)
    # ══════════════════════════════════════════════════════════════════════════
    "light": {
        # Fonds — ciel de jour progressif
        "bg_primary":   "#e8f4fd",
        "bg_secondary": "#d4ebf8",
        "bg_tertiary":  "#ffffff",
        "bg_elevated":  "#ffffff",
        "bg_card":      "#f8fbff",
        # Textes — bleu marine foncé pour contraste maximal sur fond clair
        "text":         "#0a1f33",   # quasi noir bleuté — très lisible
        "text2":        "#1a4a6e",   # bleu marine moyen
        "text3":        "#3a7ca8",   # bleu plus clair pour hints
        # Bordures
        "border_soft":  "rgba(10,60,120,0.15)",
        "border_med":   "rgba(10,60,120,0.30)",
        "border_teal":  "rgba(0,130,110,0.28)",
        # Plotly — fond blanc légèrement bleuté
        "plot_bg":      "rgba(232,244,253,0.90)",
        "grid_color":   "rgba(10,60,120,0.08)",
        "line_color":   "rgba(10,60,120,0.15)",
        # Sidebar — dégradé bleu ciel doux
        "sidebar_bg":   "linear-gradient(180deg,#d4ebf8 0%,#e8f4fd 100%)",
        # Image fond — overlay très léger pour laisser voir l'image tout en lisant
        "bg_image_overlay": "linear-gradient(145deg,rgba(200,230,250,0.88) 0%,rgba(180,215,245,0.82) 50%,rgba(200,230,250,0.88) 100%)",
        # CSS Streamlit overrides
        "streamlit_bg": "#e8f4fd",
        "streamlit_secondary_bg": "#ffffff",
        "streamlit_text": "#0a1f33",
    },
}

# Accents vifs — identiques dans les deux thèmes (bon contraste partout)
ACCENT_COLORS = {
    "teal":   "#00d4b1",
    "blue":   "#0ea5e9",
    "amber":  "#f59e0b",
    "red":    "#ef4444",
    "coral":  "#f97316",
    "green":  "#10b981",
    "purple": "#8b5cf6",
    "gray":   "#94a3b8",
    "pink":   "#ec4899",
}


def get_theme(theme_name: str = "dark") -> dict:
    """
    Retourne le dict complet du thème demandé,
    enrichi des accents communs et des alias courts.
    """
    th = dict(THEMES.get(theme_name, THEMES["dark"]))
    th.update(ACCENT_COLORS)
    th["name"] = theme_name
    # Alias courts pour compatibilité avec l'ancien code
    th["bg"]  = th["bg_primary"]
    th["bg2"] = th["bg_secondary"]
    th["bg3"] = th["bg_tertiary"]
    th["bg4"] = th["bg_elevated"]
    th["bg5"] = th["bg_card"]
    return th


def build_css(th: dict, img_url: str) -> str:
    """
    Génère le bloc CSS global Streamlit selon le thème.
    th : dict retourné par get_theme()
    img_url : URL de l'image de fond
    """
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

    * {{ box-sizing: border-box; }}
    
    /* ── Animations Sentinel Mode ── */
    @keyframes sentinel-pulse {{
        0%   {{ border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }}
        70%  {{ border-color: rgba(239, 68, 68, 0.9); box-shadow: 0 0 0 12px rgba(239, 68, 68, 0); }}
        100% {{ border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }}
    }}
    .sentinel-pulse {{
        animation: sentinel-pulse 2s infinite ease-in-out;
    }}

    /* Lueurs par niveau de risque */
    .glow-red {{ box-shadow: 0 0 25px rgba(239, 68, 68, 0.45) !important; }}
    .glow-amber {{ box-shadow: 0 0 20px rgba(245, 158, 11, 0.35) !important; }}
    .glow-coral {{ box-shadow: 0 0 22px rgba(249, 115, 22, 0.40) !important; }}
    .glow-green {{ box-shadow: 0 0 15px rgba(16, 185, 129, 0.20) !important; }}

    html, body, .stApp {{ font-family: 'Inter', sans-serif; color: {th['text']}; }}

    /* ── Fond avec image + overlay ── */
    .stApp {{
        background-image: url("{img_url}");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        min-height: 100vh;
    }}
    .stApp::before {{
        content: '';
        position: fixed;
        inset: 0;
        background: {th['bg_image_overlay']};
        z-index: 0;
        pointer-events: none;
    }}
    .block-container {{ position: relative; z-index: 1; }}
    section[data-testid="stSidebar"] {{ position: relative; z-index: 2; }}

    /* ── Contenu pleine largeur ── */
    .block-container {{
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }}
    [data-testid="stAppViewContainer"] > .main > .block-container {{
        max-width: 100% !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }}
    .stMainBlockContainer {{
        max-width: 100% !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: {th['sidebar_bg']} !important;
        border-right: 1px solid {th['border_teal']} !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider   label {{
        font-size: 11px !important;
        color: {th['text3']} !important;
        text-transform: uppercase;
        letter-spacing: .08em;
    }}

    /* ── Onglets ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {'rgba(5,21,37,0.95)' if th['name']=='dark' else 'rgba(212,235,248,0.97)'};
        border-radius: 12px; padding: 5px; gap: 3px;
        border: 1px solid {th['border_soft']};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px; padding: 8px 20px; font-size: 13px;
        color: {th['text2']}; background: transparent; border: none;
        transition: all .18s;
        font-weight: {'400' if th['name']=='dark' else '500'};
    }}
    .stTabs [aria-selected="true"] {{
        background: {'rgba(0,212,177,0.14)' if th['name']=='dark' else 'rgba(0,130,110,0.15)'} !important;
        color: {'#00d4b1' if th['name']=='dark' else '#006b58'} !important;
        border: 1px solid {'rgba(0,212,177,0.30)' if th['name']=='dark' else 'rgba(0,130,110,0.40)'} !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.2rem; }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}

    /* ── Tous les textes lisibles selon thème ── */
    p, div {{ color: {th['text']}; }}
    h1, h2, h3, h4 {{ color: {th['text']} !important; }}

    /* ══════════════════════════════════════════════════════════════════
       SIDEBAR — textes et widgets
    ══════════════════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] * {{
        color: {th['text']} !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {{
        background-color: {'#0b2540' if th['name']=='dark' else '#ffffff'} !important;
        border: 1.5px solid {th['border_med']} !important;
        border-radius: 8px !important;
        color: {th['text']} !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] div,
    section[data-testid="stSidebar"] [data-baseweb="select"] p,
    section[data-testid="stSidebar"] [data-baseweb="select"] input {{
        color: {th['text']} !important;
        background-color: transparent !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] input::placeholder {{
        color: {th['text3']} !important;
        opacity: 1 !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="tag"],
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {{
        background-color: {'rgba(0,212,177,0.18)' if th['name']=='dark' else 'rgba(0,80,64,0.12)'} !important;
        border: 1px solid {'rgba(0,212,177,0.42)' if th['name']=='dark' else 'rgba(0,80,64,0.38)'} !important;
        border-radius: 6px !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="tag"] span,
    section[data-testid="stSidebar"] [data-baseweb="tag"] svg,
    [data-testid="stMultiSelect"] [data-baseweb="tag"] span {{
        color: {'#00d4b1' if th['name']=='dark' else '#003828'} !important;
        fill:  {'#00d4b1' if th['name']=='dark' else '#003828'} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSlider"] p,
    section[data-testid="stSidebar"] [data-testid="stSlider"] span,
    section[data-testid="stSidebar"] [data-testid="stTickBarMin"],
    section[data-testid="stSidebar"] [data-testid="stTickBarMax"] {{
        color: {th['text3']} !important;
    }}

    /* ══════════════════════════════════════════════════════════════════
       MENUS DÉROULANTS — portail body-level (hors sidebar)
       BaseWeb monte les listbox dans un div portal sur le <body>.
       Les sélecteurs sidebar ne les atteignent PAS — ciblage GLOBAL.
    ══════════════════════════════════════════════════════════════════ */
    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] [data-baseweb="menu"],
    [data-baseweb="popover"] ul,
    ul[role="listbox"],
    div[role="listbox"],
    [data-baseweb="menu"] {{
        background-color: {'#071e35' if th['name']=='dark' else '#ffffff'} !important;
        border: 1px solid {th['border_med']} !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 36px rgba(0,0,0,{'0.35' if th['name']=='dark' else '0.16'}) !important;
    }}
    [data-baseweb="menu"] [role="option"],
    [data-baseweb="menu"] li,
    ul[role="listbox"] li,
    div[role="listbox"] [role="option"],
    [role="option"] {{
        background-color: {'#071e35' if th['name']=='dark' else '#ffffff'} !important;
        color: {'#c8e8f8' if th['name']=='dark' else '#0a1f33'} !important;
        font-size: 13px !important;
    }}
    [role="option"] span,
    [role="option"] div,
    [role="option"] p,
    [data-baseweb="menu"] li span,
    [data-baseweb="menu"] li div {{
        color: {'#c8e8f8' if th['name']=='dark' else '#0a1f33'} !important;
        background-color: transparent !important;
    }}
    [role="option"]:hover,
    [role="option"]:focus,
    [data-baseweb="menu"] [role="option"]:hover,
    [data-baseweb="menu"] li:hover {{
        background-color: {'rgba(0,212,177,0.14)' if th['name']=='dark' else 'rgba(10,60,120,0.09)'} !important;
    }}
    [role="option"]:hover span,
    [role="option"]:hover div,
    [role="option"]:hover p,
    [data-baseweb="menu"] li:hover span {{
        color: {'#00d4b1' if th['name']=='dark' else '#002a1e'} !important;
    }}
    [aria-selected="true"],
    [aria-selected="true"] span,
    [aria-selected="true"] div {{
        color: {'#00d4b1' if th['name']=='dark' else '#002a1e'} !important;
        font-weight: 600 !important;
        background-color: {'rgba(0,212,177,0.10)' if th['name']=='dark' else 'rgba(10,60,120,0.07)'} !important;
    }}

    /* ── Widgets ── */
    .stSelectbox [data-baseweb="select"] > div {{
        background: {'rgba(7,30,53,0.95)' if th['name']=='dark' else 'rgba(255,255,255,0.97)'} !important;
        border-color: {th['border_soft']} !important;
        border-radius: 8px !important;
        color: {th['text']} !important;
    }}
    .stSelectbox [data-baseweb="select"] span {{
        color: {th['text']} !important;
    }}
    /* Slider track */
    [data-testid="stSlider"] [data-baseweb="slider"] {{
        color: {th['text']} !important;
    }}
    .stSlider label, .stSelectbox label, .stCheckbox label {{
        color: {th['text2']} !important;
    }}
    .stCheckbox label span {{ font-size: 13px; color: {th['text2']}; }}
    .js-plotly-plot .plotly {{ background: transparent !important; }}

    /* ── Métriques Streamlit ── */
    [data-testid="stMetric"] label {{ color: {th['text2']} !important; }}
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {th['text']} !important; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: {'rgba(14,165,233,0.35)' if th['name']=='dark' else 'rgba(10,60,120,0.30)'};
        border-radius: 3px;
    }}

    /* ══════════════════════════════════════════════════════════════════
       RÈGLES CONDITIONNELLES PAR data-airsentinel-theme
       Spécificité maximale pour les portals body-level
    ══════════════════════════════════════════════════════════════════ */
    body[data-airsentinel-theme="light"] [data-baseweb="popover"] > div,
    body[data-airsentinel-theme="light"] [data-baseweb="menu"],
    body[data-airsentinel-theme="light"] [data-baseweb="menu"] ul,
    body[data-airsentinel-theme="light"] ul[role="listbox"],
    body[data-airsentinel-theme="light"] div[role="listbox"] {{
        background-color: #ffffff !important;
        border: 1px solid rgba(10,60,120,0.30) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.14) !important;
    }}
    body[data-airsentinel-theme="light"] [role="option"],
    body[data-airsentinel-theme="light"] [data-baseweb="menu"] li {{
        background-color: #ffffff !important;
        color: #0a1f33 !important;
    }}
    body[data-airsentinel-theme="light"] [role="option"] *,
    body[data-airsentinel-theme="light"] [data-baseweb="menu"] li * {{
        color: #0a1f33 !important;
        background-color: transparent !important;
    }}
    body[data-airsentinel-theme="light"] [role="option"]:hover,
    body[data-airsentinel-theme="light"] [data-baseweb="menu"] li:hover {{
        background-color: rgba(10,60,120,0.09) !important;
    }}
    body[data-airsentinel-theme="light"] [role="option"]:hover * {{
        color: #001e10 !important;
    }}

    body[data-airsentinel-theme="dark"] [data-baseweb="popover"] > div,
    body[data-airsentinel-theme="dark"] [data-baseweb="menu"],
    body[data-airsentinel-theme="dark"] [data-baseweb="menu"] ul,
    body[data-airsentinel-theme="dark"] ul[role="listbox"],
    body[data-airsentinel-theme="dark"] div[role="listbox"] {{
        background-color: #051525 !important;
        border: 1px solid rgba(14,165,233,0.28) !important;
        box-shadow: 0 10px 36px rgba(0,0,0,0.40) !important;
    }}
    body[data-airsentinel-theme="dark"] [role="option"],
    body[data-airsentinel-theme="dark"] [data-baseweb="menu"] li {{
        background-color: #051525 !important;
        color: #c8e8f8 !important;
    }}
    body[data-airsentinel-theme="dark"] [role="option"] *,
    body[data-airsentinel-theme="dark"] [data-baseweb="menu"] li * {{
        color: #c8e8f8 !important;
        background-color: transparent !important;
    }}
    body[data-airsentinel-theme="dark"] [role="option"]:hover,
    body[data-airsentinel-theme="dark"] [data-baseweb="menu"] li:hover {{
        background-color: rgba(0,212,177,0.13) !important;
    }}
    body[data-airsentinel-theme="dark"] [role="option"]:hover * {{
        color: #00d4b1 !important;
    }}
    </style>
    """
