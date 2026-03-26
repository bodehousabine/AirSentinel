"""
assets.py — AirSentinel Cameroun
Palette bleu de mer + images variées et lumineuses.
"""

IMAGES = {
    # Fond général — ciel bleu océan / satellite
    "bg_app":        "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=1920&q=60&auto=format",
    # Header — ville africaine lumineuse aérienne
    "header_banner": "https://images.unsplash.com/photo-1569974507005-6dc61f97fb5c?w=1600&q=85&auto=format",
    # Sidebar — forêt verte Cameroun
    "sidebar_top":   "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?w=400&q=80&auto=format",
    # Bloc 1 Carte — Afrique satellite lumières
    "carte_banner":  "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=85&auto=format",
    # Bloc 2 KPIs — smog ville pollution
    "kpi_banner":    "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=1200&q=85&auto=format",
    "kpi_side":      "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=600&q=80&auto=format",
    # Bloc 3 Prédictions — harmattan + ciel tropical
    "pred_harmattan":"https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&q=80&auto=format",
    "pred_banner":   "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=1200&q=85&auto=format",
    # Bloc 4 Alertes — feux + chaleur
    "alert_feux":    "https://images.unsplash.com/photo-1562155955-1cb2d73488d7?w=800&q=80&auto=format",
    "alert_chaleur": "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=800&q=80&auto=format",
    # Bloc 5 Santé — médecins Afrique
    "sante_banner":  "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=1200&q=85&auto=format",
    "sante_side":    "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=600&q=80&auto=format",
    # Bloc 6 Contexte — saisons Cameroun
    "ctx_foret":     "https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?w=600&q=80&auto=format",
    "ctx_harmattan": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=600&q=80&auto=format",
    "ctx_feux":      "https://images.unsplash.com/photo-1562155955-1cb2d73488d7?w=600&q=80&auto=format",
    "ctx_pluies":    "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=600&q=80&auto=format",
}

# ── Palette bleu de mer ───────────────────────────────────────────────────────
BG_PRIMARY   = "#020c18"   # fond principal — bleu nuit océan
BG_SECONDARY = "#051525"   # fond secondaire
BG_TERTIARY  = "#071e35"   # cartes
BG_ELEVATED  = "#0a2845"   # cartes surélevées
BG_CARD      = "#0d2f50"   # cartes interactives

BORDER_SOFT  = "rgba(14,165,233,0.14)"   # bleu ciel doux
BORDER_MED   = "rgba(14,165,233,0.28)"   # bleu ciel moyen
BORDER_TEAL  = "rgba(0,201,167,0.22)"    # teal signature


def css_bg_image(url: str = "", opacity: float = 0.08) -> str:
    """Image de fond de la ville avec overlay bleu de mer semi-transparent."""
    img = IMAGES["bg_app"]
    return f"""
    <style>
    .stApp {{
        background-image: url("{img}");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    .stApp::before {{
        content: \'\';
        position: fixed;
        inset: 0;
        background: linear-gradient(145deg,
            rgba(2,12,24,0.88) 0%,
            rgba(3,17,31,0.82) 40%,
            rgba(5,25,41,0.80) 100%);
        z-index: 0;
        pointer-events: none;
    }}
    .block-container   {{ position: relative; z-index: 1; }}
    section[data-testid="stSidebar"] {{ position: relative; z-index: 2; }}
    </style>
    """
