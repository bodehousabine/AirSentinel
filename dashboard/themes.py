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

    /* ── Sidebar filtres : lisibilité maximale dans les deux thèmes ── */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {{
        color: {th['text']} !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: {'rgba(7,30,53,0.95)' if th['name']=='dark' else 'rgba(255,255,255,0.97)'} !important;
        border-color: {th['border_soft']} !important;
        color: {th['text']} !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="select"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] div {{
        color: {th['text']} !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="tag"] {{
        background: {'rgba(0,212,177,0.15)' if th['name']=='dark' else 'rgba(0,130,110,0.15)'} !important;
        color: {th['teal']} !important;
    }}
    /* Slider labels */
    section[data-testid="stSidebar"] [data-testid="stSlider"] p {{
        color: {th['text2']} !important;
    }}
    section[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] span {{
        color: {th['text3']} !important;
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
    </style>
    """
