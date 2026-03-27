"""
landing.py — AirSentinel Cameroun
Page d'accueil : fond ville Yaoundé/stade, logo, slogan, bouton dashboard.
Fix : badges stats en HTML pur sans f-string imbriqué problématique.
"""
import streamlit as st
from assets import IMAGES
from themes import get_theme
from translations import get_t


def render_landing():
    th   = get_theme(st.session_state.get("theme_name", "dark"))
    lang = st.session_state.get("lang", "fr")
    T    = get_t(lang)

    # Image de fond = image ville avec stade (bg_app)
    bg_url = IMAGES["bg_app"]

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp {{
        background-image: url("{bg_url}");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    .stApp::before {{
        content: '';
        position: fixed;
        inset: 0;
        background: linear-gradient(160deg,
            rgba(2,12,24,0.91) 0%,
            rgba(3,18,35,0.84) 45%,
            rgba(2,14,28,0.88) 100%);
        z-index: 0;
        pointer-events: none;
    }}
    .block-container {{
        position: relative; z-index: 1;
        padding-top: 0 !important;
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }}
    section[data-testid="stSidebar"] {{ display: none !important; }}
    header[data-testid="stHeader"]   {{ display: none !important; }}
    footer {{ display: none !important; }}

    .landing-btn > button {{
        background: linear-gradient(135deg, #00d4b1 0%, #0ea5e9 100%) !important;
        color: #020c18 !important;
        border: none !important;
        border-radius: 50px !important;
        height: 56px !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        letter-spacing: .05em !important;
        box-shadow: 0 8px 36px rgba(0,212,177,0.40) !important;
        transition: all .2s !important;
        width: 100% !important;
        font-family: 'Inter', sans-serif !important;
    }}
    .landing-btn > button:hover {{
        box-shadow: 0 14px 44px rgba(0,212,177,0.55) !important;
        transform: translateY(-3px) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='min-height:8vh;'></div>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])

    with col:
        # Logo
        st.markdown("""
        <div style="text-align:center;margin-bottom:12px;">
            <div style="font-size:84px;line-height:1;
                        filter:drop-shadow(0 6px 28px rgba(0,212,177,0.55));">🌍</div>
        </div>""", unsafe_allow_html=True)

        # Nom
        st.markdown("""
        <div style="text-align:center;margin-bottom:8px;">
            <span style="font-size:56px;font-weight:700;color:#e0f2fe;
                         letter-spacing:-.03em;font-family:'Inter',sans-serif;
                         text-shadow:0 4px 32px rgba(0,212,177,0.20);">Air</span>
            <span style="font-size:56px;font-weight:700;color:#00d4b1;
                         letter-spacing:-.03em;font-family:'Inter',sans-serif;
                         text-shadow:0 6px 36px rgba(0,212,177,0.45);">Sentinel</span>
        </div>""", unsafe_allow_html=True)

        # Sous-titre
        subtitle = "CAMEROUN · 2020–2025" if lang == "fr" else "CAMEROON · 2020–2025"
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:24px;">
            <span style="font-size:13px;color:#00d4b1;letter-spacing:.22em;
                         text-transform:uppercase;font-family:'DM Mono',monospace;">
                {subtitle}
            </span>
        </div>""", unsafe_allow_html=True)

        # Séparateur
        st.markdown("""
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
            <div style="flex:1;height:1px;background:linear-gradient(to right,transparent,rgba(0,212,177,0.45));"></div>
            <div style="width:7px;height:7px;border-radius:50%;background:#00d4b1;
                        box-shadow:0 0 10px rgba(0,212,177,0.6);"></div>
            <div style="flex:1;height:1px;background:linear-gradient(to left,transparent,rgba(0,212,177,0.45));"></div>
        </div>""", unsafe_allow_html=True)

        # Slogan
        slogan = "Anticiper. Alerter. Protéger." if lang == "fr" else "Anticipate. Alert. Protect."
        desc = (
            "Système d'aide à la décision sanitaire basé sur l'IA<br>40 villes · 10 régions · 50 760 observations"
            if lang == "fr" else
            "AI-powered health decision support system<br>40 cities · 10 regions · 50,760 observations"
        )
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:10px;">
            <div style="font-size:30px;font-weight:600;color:#e0f2fe;
                        letter-spacing:.02em;line-height:1.3;font-family:'Inter',sans-serif;
                        text-shadow:0 2px 18px rgba(0,0,0,0.6);">{slogan}</div>
        </div>
        <div style="text-align:center;margin-bottom:32px;">
            <div style="font-size:14px;color:rgba(224,242,254,0.60);
                        line-height:1.7;max-width:440px;margin:0 auto;">{desc}</div>
        </div>""", unsafe_allow_html=True)

        # Badges stats — construits séparément pour éviter le bug de parsing
        lbl_villes  = "villes"      if lang == "fr" else "cities"
        lbl_regions = "régions"     if lang == "fr" else "regions"
        lbl_obs     = "observations"
        lbl_pred    = "prédictions" if lang == "fr" else "predictions"

        badge = lambda val, lbl: f"""
            <div style="background:rgba(255,255,255,0.07);
                        border:1px solid rgba(0,212,177,0.25);
                        border-radius:12px;padding:12px 20px;text-align:center;
                        backdrop-filter:blur(10px);">
                <div style="font-size:22px;font-weight:700;color:#00d4b1;
                            font-family:'Inter',sans-serif;">{val}</div>
                <div style="font-size:11px;color:rgba(224,242,254,0.55);
                            margin-top:3px;letter-spacing:.06em;">{lbl}</div>
            </div>"""

        badges_html = (
            '<div style="display:flex;justify-content:center;gap:12px;'
            'flex-wrap:wrap;margin-bottom:38px;">'
            + badge("40",     lbl_villes)
            + badge("10",     lbl_regions)
            + badge("50 760", lbl_obs)
            + badge("4",      lbl_pred)
            + "</div>"
        )
        st.markdown(badges_html, unsafe_allow_html=True)

        # Bouton entrée
        btn_label = "🚀  Accéder au Dashboard  →" if lang == "fr" else "🚀  Open Dashboard  →"
        st.markdown('<div class="landing-btn">', unsafe_allow_html=True)
        enter = st.button(btn_label, key="enter_dashboard", width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

        # Footer équipe
        st.markdown("""
        <div style="text-align:center;margin-top:30px;">
            <div style="font-size:11px;color:rgba(224,242,254,0.30);
                        font-family:'DM Mono',monospace;letter-spacing:.06em;line-height:2.2;">
                IndabaX Cameroon 2026 · DPA Green Tech<br>
                ISSEA · ENSP Yaoundé ·
                <span style="color:rgba(0,212,177,0.55);">17 mars → 7 avril 2026</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='min-height:6vh;'></div>", unsafe_allow_html=True)
    return enter
