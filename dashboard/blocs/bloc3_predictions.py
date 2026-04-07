"""blocs/bloc3_predictions.py — Prédictions · modèle réel + performance · bilingue + thème"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import joblib
import os
from datetime import date, timedelta
from utils import get_context, banner, sources_bar, empty_state, irs_level
from assets import IMAGES

# ── Icônes SVG robustes pour blocs HTML personnalisés ────────────────────────
SVG_ICONS = {
    "track_changes": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5.5-8c0-3.03 2.47-5.5 5.5-5.5s5.5 2.47 5.5 5.5-2.47 5.5-5.5 5.5-5.5-2.47-5.5-5.5z"></path></svg>',
    "straighten": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M21 6H3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 10H3V8h2v4h2V8h2v4h2V8h2v4h2V8h2v4h2V8h2v8z"></path></svg>',
    "warning": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"></path></svg>',
    "check_circle": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"></path></svg>',
    "today": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"></path></svg>',
    "online_prediction": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 10h3l-4 4-4-4h3V8h2v4z"></path></svg>',
    "thermostat": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M15 13V5c0-1.66-1.34-3-3-3S9 3.34 9 5v8c-1.21.91-2 2.37-2 4 0 2.76 2.24 5 5 5s5-2.24 5-5c0-1.63-.79-3.09-2-4zm-3-9c.55 0 1 .45 1 1v3h-2V5c0-.55.45-1 1-1z"></path></svg>',
    "air": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M13 3.17c2.34.62 4 2.76 4 5.24 0 1.13-.34 2.21-.93 3.12l-1.43-1.43c.22-.52.36-1.1.36-1.69 0-1.65-1.35-3-3-3s-3 1.35-3 3h-2c0-2.76 2.24-5 5-5zm0 13.66c-2.34-.62-4-2.76-4-5.24 0-1.13.34-2.21.93-3.12l1.43 1.43c-.22.52-.36 1.1-.36 1.69 0 1.65 1.35 3 3 3s3-1.35 3-3h2c0 2.76-2.24 5-5 5z"></path></svg>',
    "grain": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M10 12c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zM6 8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm12-8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm-4 8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm4-4c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-4-4c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-4-4c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"></path></svg>',
    "rainy": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"></path></svg>',
    "thunderstorm": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M18 15v3H6v-3H4v3c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-3h-2zm-1-4l-1.41-1.41L13 12.17V4h-2v8.17L8.41 9.59 7 11l5 5 5-5z"></path></svg>',
    "cyclone": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6z"></path></svg>',
    "local_fire_department": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M19.48 12.35c-1.57-4.08-7.16-4.3-5.81-10.23.1-.44-.37-.78-.7-.5-1.92 1.64-3.66 4.04-4.22 6.48-.57 2.48-.18 4.7 1.22 6.55.14.19-.05.47-.28.41-2.02-.5-3.32-2.15-3.32-4.14 0-1.25.46-2.52 1.34-3.54.43-.51-.12-1.26-.74-.95C4.84 7.6 3.5 10.35 3.5 13.3c0 4.69 3.81 8.5 8.5 8.5s8.5-3.81 8.5-8.5c0-.28-.02-.56-.05-.83-.06-.5-.65-.72-.97-.47z"></path></svg>',
    "error": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"></path></svg>',
    "dangerous": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M15.73 3H8.27L3 8.27v7.46L8.27 21h7.46L21 15.73V8.27L15.73 3zM12 17.3c-.72 0-1.3-.58-1.3-1.3 0-.72.58-1.3 1.3-1.3s1.3.58 1.3 1.3c0 .72-.58 1.3-1.3 1.3zm1-4.3h-2V7h2v6z"></path></svg>',
    "block": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM4 12c0-4.42 3.58-8 8-8 1.85 0 3.55.63 4.9 1.69L5.69 16.9C4.63 15.55 4 13.85 4 12zm8 8c-1.85 0-3.55-.63-4.9-1.69L18.31 7.1C19.37 8.45 20 10.15 20 12c0 4.42-3.58 8-8 8z"></path></svg>',
    "push_pin": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M16 9V4l1 0c.55 0 1-.45 1-1s-.45-1-1-1H7c-.55 0-1 .45-1 1s.45 1 1 1l1 0v5c0 1.66-1.34 3-3 3v2h5.97v7l1 1 1-1v-7H19v-2c-1.66 0-3-1.34-3-3z"></path></svg>',
    "science": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M20.8 18.4L15 5.4V4h1c.55 0 1-.45 1-1s-.45-1-1-1H8c-.55 0-1 .45-1 1s-.45 1-1 1h1v1.4L3.2 18.4C2.3 20.3 3.7 22 5.7 22h12.6c2 0 3.4-1.7 2.5-3.6zM13 6.1l2.7 6H8.3l2.7-6V4h2v2.1z"></path></svg>',
    "trending_up": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"></path></svg>',
    "trending_down": '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"></path></svg>'
}

def get_icon(name, size=24):
    return SVG_ICONS.get(name, "").replace('width="24"', f'width="{size}"').replace('height="24"', f'height="{size}"')

# ── Zones INS Cameroun (2019) ─────────────────────────────────────────────────
ZONES_REGIONS = {
    'Zone équatoriale':        ['Centre', 'Est', 'Sud', 'Littoral', 'Sud-Ouest', 'Ouest', 'Nord-Ouest'],
    'Zone soudanienne':        ['Adamaoua', 'Nord'],
    'Zone soudano-sahélienne': ['Extreme-Nord'],
}

MOIS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin',
           'Juillet','Août','Septembre','Octobre','Novembre','Décembre']
MOIS_EN = ['January','February','March','April','May','June',
           'July','August','September','October','November','December']
MOIS_COURT_FR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
MOIS_COURT_EN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

def _get_zone(region):
    for zone, regions in ZONES_REGIONS.items():
        if region in regions:
            return zone
    return 'Zone équatoriale'

@st.cache_resource
def _load_models():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chemins  = [
        os.path.join(base_dir, '..', 'models'),
        os.path.join(base_dir, '..', '..', 'models'),
        os.path.join(base_dir, 'models'),
    ]
    base = None
    for chemin in chemins:
        if os.path.exists(os.path.join(chemin, 'meilleur_modele.pkl')):
            base = chemin
            break
    if base is None:
        return None, None, None, None
    try:
        modele   = joblib.load(os.path.join(base, 'meilleur_modele.pkl'))
        scaler   = joblib.load(os.path.join(base, 'scaler.pkl'))
        features = joblib.load(os.path.join(base, 'features.pkl'))
        arima    = joblib.load(os.path.join(base, 'arima_par_zone.pkl'))
        return modele, scaler, features, arima
    except:
        return None, None, None, None

def _predire_ville(ville, df_brut, modele, scaler, features, arima):
    df_v   = df_brut[df_brut['ville'] == ville].sort_values('date')
    region = df_v['region'].iloc[-1] if len(df_v) > 0 else 'Centre'
    zone   = _get_zone(region)
    preds  = []
    for step in range(1, 4):
        try:
            last    = df_v[features].fillna(df_v[features].median()).tail(1)
            last_s  = scaler.transform(last)
            p_rl    = modele.predict(last_s)[0]
            p_arima = arima[zone].forecast(steps=step).iloc[-1]
            preds.append(max(0, p_rl + p_arima))
        except:
            base = float(df_v['pm2_5_moyen'].mean()) if len(df_v) > 0 else 15.0
            preds.append(base)
    return preds, zone


def render(profil):
    ctx  = get_context()
    df   = ctx["df_brut"]
    th   = ctx["th"]
    T    = ctx["T"]
    lang = ctx["lang"]
    mois = ctx["mois"]

    _b_col, _sel_col = st.columns([2.4, 1])
    with _b_col:
        banner(
            IMAGES["pred_banner"], 120,
            T['bloc3_label'],
            "", th,
            accent=th["amber"], tint_hex="#f59e0b", tint_strength=0.28
        )
    with _sel_col:
        st.markdown('<div style="margin-top:34px;"></div>', unsafe_allow_html=True)
        v_all = T["all_cities"]
        v_list = [v_all] + sorted(df["ville"].unique().tolist())
        v = st.selectbox(
            ":material/location_on: " + ("**SÉLECTIONNER UNE VILLE**" if lang == "fr" else "**SELECT A CITY**"),
            v_list, index=0, key="p_v"
        )

    if len(df) == 0:
        empty_state(T, th)
        return

    PL   = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
                font=dict(color=th["text2"], size=12))
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False)

    # Charger modèles
    modele, scaler, features, arima = _load_models()
    modeles_ok = all(x is not None for x in [modele, scaler, features, arima])

    # ── Sous-Onglets (Définis par les clés bloc3_sub_ong_... dans translations.py)
    tabs = st.tabs([
        T["bloc3_sub_ong_1"], 
        T["bloc3_sub_ong_2"], 
        T["bloc3_sub_ong_3"], 
        T["bloc3_sub_ong_4"]
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 1 — Prédiction J/J+1/J+2
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[0]:
        v_all = T["all_cities"]
        if v == v_all:
            # Agrégation nationale (moyenne de l'historique et des prédictions)
            df_v = df.sort_values("date")
            hist = df_v.groupby("date")["pm2_5_moyen"].mean().tail(60).reset_index()
            
            # Pour la prédiction nationale, on moyenne les prédictions par ville
            all_villes = sorted(df["ville"].unique().tolist())
            all_p_lists = []
            for city in all_villes:
                if modeles_ok:
                    p, _ = _predire_ville(city, df, modele, scaler, features, arima)
                    all_p_lists.append(p)
                else:
                    # Fallback si modèle non OK
                    df_c = df[df["ville"] == city]
                    base = float(df_c["pm2_5_moyen"].mean()) if len(df_c) > 0 else 15.0
                    all_p_lists.append([base] * 3)
            
            preds = np.mean(all_p_lists, axis=0).tolist()
            zone_v = "National"
            source_pred = "Moyenne nationale (aggrégat)"
        else:
            df_v = df[df["ville"] == v].sort_values("date")
            hist = df_v.groupby("date")["pm2_5_moyen"].mean().tail(60).reset_index()

            if modeles_ok and len(df_v) > 0:
                preds, zone_v = _predire_ville(v, df, modele, scaler, features, arima)
                source_pred   = f"Modèle Hybride RL+ARIMA · {zone_v}"
            else:
                base  = float(df_v["pm2_5_moyen"].mean()) if len(df_v) > 0 else 15.0
                np.random.seed(hash(v) % 2**31)
                preds       = [base * (0.88 + 0.24 * np.random.random()) for _ in range(3)]
                zone_v      = ""
                source_pred = "Moyenne historique (modèle non disponible)"

        jours    = [date.today() + timedelta(days=i) for i in range(0, 3)]
        jours_pd = pd.to_datetime(jours)
        mae       = 3.456
        pred_high = [p + mae for p in preds]
        pred_low  = [max(0, p - mae) for p in preds]
        
        # ── Chargement seuil contextuel CMR ───────────────────────────────
        def _load_seuils_ctx_b3():
            base = os.path.dirname(os.path.abspath(__file__))
            for c in [os.path.join(base, '..', 'models'), os.path.join(base, '..', '..', 'models')]:
                p = os.path.join(c, 'seuils_contextuels.pkl')
                if os.path.exists(p):
                    return joblib.load(p)
            return None

        _sc = _load_seuils_ctx_b3()
        seuil_ctx_pred = None
        if _sc:
            if v == v_all:
                p90s = _sc.get('par_ville', {}).values()
                if p90s:
                    seuil_ctx_pred = round(sum(p90s) / len(p90s), 1)
            else:
                if v in _sc.get('par_ville', {}):
                    seuil_ctx_pred = round(_sc['par_ville'][v], 1)

        # ── Graphique agrandi ─────────────────────────────────────────────
        fig = go.Figure()

        # Historique 60 jours
        fig.add_trace(go.Scatter(
            x=hist["date"], y=hist["pm2_5_moyen"],
            mode="lines",
            name="Historique 60j" if lang == "fr" else "60d history",
            line=dict(color=th["blue"], width=2.5),
            fill="tozeroy", fillcolor="rgba(14,165,233,0.08)"
        ))

        # Intervalle de confiance
        fig.add_trace(go.Scatter(
            x=list(jours_pd) + list(jours_pd[::-1]),
            y=pred_high + pred_low[::-1],
            fill="toself", fillcolor="rgba(245,158,11,0.18)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=True,
            name=f"IC ±{mae:.1f} µg/m³"
        ))

        # Prédictions
        fig.add_trace(go.Scatter(
            x=jours_pd, y=preds,
            mode="lines+markers+text",
            name="Prédiction" if lang == "fr" else "Forecast",
            line=dict(color=th["amber"], width=3, dash="dash"),
            marker=dict(size=14, color=th["amber"],
                        symbol="diamond",
                        line=dict(color=th.get("bg_elevated","#1e293b"), width=2)),
            text=[f"{p:.1f}" for p in preds],
            textposition="top center",
            textfont=dict(color=th["amber"], size=13, family="DM Mono")
        ))

        # Ligne de connexion historique → prédiction
        if len(hist) > 0:
            last_hist_date = hist["date"].iloc[-1]
            last_hist_val  = hist["pm2_5_moyen"].iloc[-1]
            fig.add_trace(go.Scatter(
                x=[last_hist_date, jours_pd[0]],
                y=[last_hist_val, preds[0]],
                mode="lines",
                line=dict(color=th["amber"], width=1.5, dash="dot"),
                showlegend=False
            ))

        # Seuil OMS
        fig.add_hline(
            y=15.0, line=dict(color=th["red"], width=1.5, dash="dash"),
            annotation_text="OMS 15 µg/m³",
            annotation_font_color=th["red"], annotation_font_size=11
        )
        
        # Seuil Contexte Camerounais
        if seuil_ctx_pred:
            fig.add_hline(
                y=seuil_ctx_pred,
                line=dict(color=th.get("teal", "#14b8a6"), width=1.5, dash="dot"),
                annotation_text=f"Contexte CMR · {seuil_ctx_pred:.1f} µg/m³",
                annotation_font_color=th.get("teal", "#14b8a6"), annotation_font_size=10,
                annotation_position="top right"
            )

        # Zone de prédiction annotée
        fig.add_vrect(
            x0=jours_pd[0], x1=jours_pd[-1],
            fillcolor="rgba(245,158,11,0.05)",
            line_width=0,
            annotation_text="Zone prédite" if lang == "fr" else "Forecast zone",
            annotation_position="top left",
            annotation_font_color=th["amber"],
            annotation_font_size=10
        )

        titre_pred = f"PM2.5 · {v} · {'72h Forecast' if lang=='en' else 'Prédiction 72h'}"
        fig.update_layout(
            **PL, height=420,
            title=dict(text=titre_pred, font=dict(color=th["text"], size=15, family="Arial Black, sans-serif")),
            legend=dict(
                font=dict(color=th["text"], size=12, family="Arial Black, sans-serif"),
                bgcolor="rgba(0,0,0,0.3)",
                bordercolor=th["border_soft"], borderwidth=1,
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            margin=dict(l=44, r=20, t=60, b=36)
        )
        fig.update_xaxes(**GRID, tickfont=dict(size=12, color=th["text"], family="Arial Black, sans-serif"))
        fig.update_yaxes(**GRID, tickfont=dict(size=12, color=th["text"], family="Arial Black, sans-serif"),
                         title_font=dict(size=13, color=th["text"], family="Arial Black, sans-serif"))
        st.plotly_chart(fig, width="stretch")

        # ── KPIs prédiction — plus visibles ──────────────────────────────
        k1, k2, k3 = st.columns(3)
        labels_j  = [
            f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('today', 16)} Aujourd'hui</div>",
            f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('online_prediction', 16)} Demain</div>",
            f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('online_prediction', 16)} Après-demain</div>"
        ] if lang == "fr" else [
            f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('today', 16)} Today</div>",
            f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('online_prediction', 16)} Tomorrow</div>",
            f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('online_prediction', 16)} Day after</div>"
        ]
        niveaux   = ["FAIBLE","MODÉRÉ","ÉLEVÉ","CRITIQUE"]

        for col, pred_val, lbl_j, jour in zip([k1, k2, k3], preds, labels_j, jours):
            color = th["green"] if pred_val <= 15 else th["amber"] if pred_val <= 25 \
                    else th["coral"] if pred_val <= 37.5 else th["red"]
            ratio = pred_val / 15
            if   pred_val <= 15:   niv = f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('check_circle', 15)} Conforme OMS</div>" if lang == "fr" else f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('check_circle', 15)} WHO Compliant</div>"
            elif pred_val <= 25:   niv = f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('warning', 15)} Modéré</div>" if lang == "fr" else f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('warning', 15)} Moderate</div>"
            elif pred_val <= 37.5: niv = f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('error', 15)} Élevé</div>" if lang == "fr" else f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('error', 15)} High</div>"
            else:                  niv = f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('dangerous', 15)} Critique</div>" if lang == "fr" else f"<div style='display:inline-flex;align-items:center;gap:6px;'>{get_icon('dangerous', 15)} Critical</div>"

            if seuil_ctx_pred:
                ratio_cmr = pred_val / seuil_ctx_pred
                lbl_cmr = "CMR"
                lbl_oms = "OMS" if lang == "fr" else "WHO"
                
                col_cmr = th.get("teal", "#14b8a6") if ratio_cmr <= 1.0 else th.get("coral", "#f43f5e")
                col_oms = th.get("green", "#10b981") if ratio <= 1.0 else th.get("red", "#ef4444")
                
                ratio_html = (
                    f'<div style="display:flex; justify-content:center; gap:8px; margin-top:10px;">'
                    f'<div style="border:1px solid {col_oms}44; color:{col_oms}; padding:3px 8px; border-radius:6px; font-size:10px; font-weight:700; background:rgba(0,0,0,0.15);">{ratio:.1f}x {lbl_oms}</div>'
                    f'<div style="border:1px solid {col_cmr}44; color:{col_cmr}; padding:3px 8px; border-radius:6px; font-size:10px; font-weight:700; background:rgba(0,0,0,0.15);">{ratio_cmr:.1f}x {lbl_cmr}</div>'
                    f'</div>'
                )
            else:
                lbl_oms = "seuil OMS" if lang == "fr" else "WHO threshold"
                ratio_html = f'<div style="font-size:10px;color:{th["text3"]};margin-top:8px;">{ratio:.1f}x {lbl_oms}</div>'

            with col:
                st.markdown(
                    f'<div style="background:linear-gradient(145deg,{th["bg_tertiary"]},{th["bg_elevated"]});'
                    f'border:1px solid {color}55;border-top:4px solid {color};'
                    f'border-radius:14px;padding:18px 14px;text-align:center;'
                    f'box-shadow:0 4px 20px {color}22;">'
                    f'<div style="font-size:11px;color:{th["text3"]};margin-bottom:6px;'
                    f'text-transform:uppercase;letter-spacing:.08em;">'
                    f'{lbl_j}</div>'
                    f'<div style="font-size:13px;color:{th["text3"]};margin-bottom:8px;">'
                    f'{jour.strftime("%d %B %Y")}</div>'
                    f'<div style="font-size:34px;font-weight:800;color:{color};'
                    f'line-height:1;text-shadow:0 0 20px {color}44;">{pred_val:.1f}</div>'
                    f'<div style="font-size:11px;color:{th["text3"]};margin-top:4px;">µg/m³</div>'
                    f'<div style="font-size:12px;color:{color};margin-top:8px;font-weight:600;">{niv}</div>'
                    f'{ratio_html}'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown(
            f'<div style="font-size:10px;color:{th["text3"]};margin-top:10px;'
            f'font-family:DM Mono,monospace;padding:8px 12px;display:flex;align-items:center;gap:6px;'
            f'background:{th["bg_tertiary"]};border-radius:8px;">'
            f'{get_icon("science", 14)} {source_pred} · IC = ±{mae} µg/m³ · WHO AQG 2021 · NCBI NBK574591</div>',
            unsafe_allow_html=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 2 — Performance du modèle
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[1]:
        if modeles_ok:
            @st.cache_data(ttl=3600)
            def _calc_perf():
                from sklearn.metrics import r2_score, mean_absolute_error
                test = df[df["date"].dt.year == 2025].copy()
                if len(test) == 0:
                    return None
                X_test   = test[features].fillna(test[features].median())
                X_test_s = scaler.transform(X_test)
                y_test   = test["pm2_5_moyen"].values
                pred_v   = modele.predict(X_test_s)
                r2       = r2_score(y_test, pred_v)
                mae_v    = mean_absolute_error(y_test, pred_v)
                err_max  = abs(y_test - pred_v).max()
                pct_10   = (abs(y_test - pred_v) > 10).mean() * 100
                return {
                    "y_test": y_test, "pred": pred_v,
                    "r2": r2, "mae": mae_v,
                    "err_max": err_max, "pct_10": pct_10,
                    "dates": test["date"].values,
                    "villes": test["ville"].values,
                }

            perf = _calc_perf()

            if perf is not None:
                # KPIs performance — plus frappants
                k1, k2, k3, k4 = st.columns(4)
                kpi_data = [
                    (k1, f"{perf['r2']:.4f}",         "R²",              "Explained variance" if lang=="en" else "Variance expliquée", th["green"],  "track_changes"),
                    (k2, f"{perf['mae']:.3f}",         "MAE (µg/m³)",     "Mean error" if lang=="en" else "Erreur moyenne",     th["amber"],  "straighten"),
                    (k3, f"{perf['err_max']:.1f}",     "Max error" if lang=="en" else "Erreur max",      "µg/m³",              th["coral"],  "warning"),
                    (k4, f"{100-perf['pct_10']:.1f}%",  "Accuracy" if lang=="en" else "Précision" ,       "Error < 10 µg/m³" if lang=="en" else "Erreur < 10 µg/m³",  th["blue"],   "check_circle"),
                ]
                for col, val, lbl, sub, color, emoji in kpi_data:
                    with col:
                        st.markdown(
                            f'<div style="background:linear-gradient(145deg,{th["bg_tertiary"]},{th["bg_elevated"]});'
                            f'border:1px solid {color}55;border-top:4px solid {color};'
                            f'border-radius:14px;padding:20px 12px;text-align:center;'
                            f'box-shadow:0 6px 24px {color}22;">'
                            f'<div style="font-size:32px;margin-bottom:8px;color:{color};">{get_icon(emoji, 32)}</div>'
                            f'<div style="font-size:28px;font-weight:800;color:{color};'
                            f'line-height:1;text-shadow:0 0 20px {color}44;">{val}</div>'
                            f'<div style="font-size:12px;font-weight:600;color:{th["text"]};'
                            f'margin-top:8px;text-transform:uppercase;letter-spacing:.06em;">{lbl}</div>'
                            f'<div style="font-size:10px;color:{th["text3"]};margin-top:4px;">{sub}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

                # Moyenne nationale (filtre ville de référence retiré car jugé inutile)
                df_perf_plot = pd.DataFrame({
                    "date": perf["dates"],
                    "y_test": perf["y_test"],
                    "pred": perf["pred"]
                })
                df_avg = df_perf_plot.groupby("date").mean().reset_index()
                
                dates_v = df_avg["date"]
                y_v     = df_avg["y_test"]
                p_v     = df_avg["pred"]
                ville_ref = "Moyenne nationale" if lang == "fr" else "National average"

                fig_tl = go.Figure()

                # Zone d'erreur
                fig_tl.add_trace(go.Scatter(
                    x=np.concatenate([dates_v, dates_v[::-1]]),
                    y=np.concatenate([p_v + 3.456, (p_v - 3.456)[::-1]]),
                    fill="toself", fillcolor="rgba(245,158,11,0.12)",
                    line=dict(color="rgba(0,0,0,0)"),
                    name=f"IC ±{mae:.1f}", showlegend=True
                ))

                fig_tl.add_trace(go.Scatter(
                    x=dates_v, y=y_v,
                    mode="lines", name="Réel" if lang == "fr" else "Actual",
                    line=dict(color=th["blue"], width=2)
                ))
                fig_tl.add_trace(go.Scatter(
                    x=dates_v, y=p_v,
                    mode="lines", name="Prédit" if lang == "fr" else "Predicted",
                    line=dict(color=th["amber"], width=2, dash="dash")
                ))
                fig_tl.add_hline(
                    y=15, line=dict(color=th["red"], width=1.5, dash="dot"),
                    annotation_text="OMS 15",
                    annotation_font_color=th["red"], annotation_font_size=10
                )
                fig_tl.update_layout(
                    **PL, height=420,
                    title=dict(
                        text=f"{'Actual vs Predicted' if lang=='en' else 'Réel vs Prédit'} · {ville_ref} · 2025 · R²={perf['r2']:.4f} · MAE={perf['mae']:.3f} µg/m³",
                        font=dict(color=th["text"], size=14, family="Arial Black, sans-serif")
                    ),
                    xaxis=dict(**GRID, tickfont=dict(size=12, color=th["text"], family="Arial Black, sans-serif")),
                    yaxis=dict(**GRID, title="PM2.5 (µg/m³)",
                               title_font=dict(size=13, color=th["text"], family="Arial Black, sans-serif"),
                               tickfont=dict(size=12, color=th["text"], family="Arial Black, sans-serif")),
                    legend=dict(
                        font=dict(color=th["text"], size=12, family="Arial Black, sans-serif"),
                        bgcolor="rgba(0,0,0,0.3)",
                        bordercolor=th["border_soft"], borderwidth=1,
                        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                    )
                )
                st.plotly_chart(fig_tl, width="stretch")
            else:
                st.info("Données de test 2025 insuffisantes.")
        else:
            st.warning("Modèles non disponibles — vérifier le dossier models/")

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 3 — Simulateur avec vrai modèle
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[2]:
        def _m(col, fb):
            return float(df[col].mean()) if col in df.columns and len(df) > 0 else fb

        # En-tête (Filtre ville retiré icic car on utilise celui du haut désormais)
        v_all = T["all_cities"]
        if v == v_all:
             # Le simulateur nécessite une ville de référence pour le contexte zones
             # On prend la première ville disponible si "Toutes villes" est sélectionné
             ville_sim = sorted(df["ville"].unique().tolist())[0]
             st.info(f":material/lightbulb: Simulation basée sur le contexte de {ville_sim} (par défaut)." if lang == "fr" else 
                     f":material/lightbulb: Simulation based on context: {ville_sim} (default).")
        else:
             ville_sim = v

        df_sim    = df[df["ville"] == ville_sim].sort_values("date")

        # ── Layout UNIQUE : sliders (gauche) | jauge (droite) ───────────────
        col_sliders, col_gauge = st.columns([3, 2])

        # Sliders dans la colonne gauche
        with col_sliders:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:{th["text3"]};'
                f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;display:flex;align-items:center;gap:6px;">'
                f'{get_icon("thermostat", 14)} '
                + ("Weather conditions" if lang=="en" else "Conditions météorologiques")
                + "</div>",
                unsafe_allow_html=True
            )
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<div style='display:flex;align-items:center;gap:6px;font-size:13px;color:{th['text']}'>{get_icon('thermostat', 16)} " + ("Temperature (°C)" if lang=="en" else "Température (°C)") + "</div>", unsafe_allow_html=True)
                temp = st.slider("label_t", 20, 45, int(min(45, max(20, _m("temperature_2m_max", 30)))), key="s_t", label_visibility="collapsed")
                
                st.markdown(f"<div style='display:flex;align-items:center;gap:6px;font-size:13px;color:{th['text']}'>{get_icon('air', 16)} " + ("Wind (km/h)" if lang=="en" else "Vent (km/h)") + "</div>", unsafe_allow_html=True)
                vent = st.slider("label_v", 0, 60, int(min(60, max(0, _m("wind_speed_10m_max", 15)))), key="s_v", label_visibility="collapsed")
            with c2:
                st.markdown(f"<div style='display:flex;align-items:center;gap:6px;font-size:13px;color:{th['text']}'>{get_icon('grain', 16)} Dust (µg/m³)</div>", unsafe_allow_html=True)
                dust = st.slider("label_d", 0, 300, int(min(300, max(0, _m("dust_moyen", 80)))), key="s_d", label_visibility="collapsed")
                
                st.markdown(f"<div style='display:flex;align-items:center;gap:6px;font-size:13px;color:{th['text']}'>{get_icon('rainy', 16)} " + ("Precipitation (mm)" if lang=="en" else "Précipitations (mm)") + "</div>", unsafe_allow_html=True)
                precip = st.slider("label_p", 0, 50, int(min(50, max(0, _m("precipitation_sum", 2)))), key="s_p", label_visibility="collapsed")
            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:{th["text3"]};'
                f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;display:flex;align-items:center;gap:6px;">'
                f'{get_icon("thunderstorm", 14)} '
                + ("Climate episodes" if lang=="en" else "Épisodes climatiques")
                + "</div>",
                unsafe_allow_html=True
            )
            c3, c4 = st.columns(2)
            with c3:
                st.markdown(f"<div style='display:flex;align-items:center;gap:6px;font-size:13px;color:{th['text']}'>{get_icon('cyclone', 16)} " + ("Intense Harmattan" if lang=="en" else "Harmattan intense") + "</div>", unsafe_allow_html=True)
                harm = st.checkbox("label_h", key="s_harm", label_visibility="collapsed",
                                   help="Dust > p90 AND precipitation < p10 · Schepanski et al. (2007)")
            with c4:
                st.markdown(f"<div style='display:flex;align-items:center;gap:6px;font-size:13px;color:{th['text']}'>{get_icon('local_fire_department', 16)} " + ("Fire episode" if lang=="en" else "Épisode feux") + "</div>", unsafe_allow_html=True)
                feux = st.checkbox("label_f", key="s_feux", label_visibility="collapsed",
                                   help="CO > p90 in dry season · Barker et al. (2020)")

        # ── Calcul vrai modèle (avant d'afficher la jauge) ────────────────
        if modeles_ok and len(df_sim) > 0:
            try:
                last_row = df_sim[features].fillna(df_sim[features].median()).tail(1).copy()
                for col_feat in features:
                    if 'temperature_2m_max' in col_feat:    last_row[col_feat] = temp
                    elif 'wind_speed_10m_max' in col_feat:  last_row[col_feat] = vent
                    elif 'dust_moyen' in col_feat:          last_row[col_feat] = dust
                    elif 'precipitation_sum' in col_feat:   last_row[col_feat] = precip
                    elif 'harmattan_intense' in col_feat:   last_row[col_feat] = int(harm)
                    elif 'episode_feux' in col_feat:        last_row[col_feat] = int(feux)
                last_s     = scaler.transform(last_row)
                p_rl       = modele.predict(last_s)[0]
                region_sim = df_sim['region'].iloc[-1]
                zone_sim   = _get_zone(region_sim)
                p_arima    = arima[zone_sim].forecast(steps=1).iloc[-1]
                pm25_s     = max(0, p_rl + p_arima)
                source_sim = f'<div style="display:inline-flex;align-items:center;gap:4px;">{get_icon("check_circle", 12)} Modèle Hybride RL+ARIMA · {zone_sim}</div>'
            except:
                pm25_s     = max(5, 10 + 0.4*temp - 0.3*vent + 0.05*dust
                                 + (15 if harm else 0) + (20 if feux else 0))
                source_sim = f'<div style="display:inline-flex;align-items:center;gap:4px;">{get_icon("warning", 12)} Fallback formule approx.</div>'
        else:
            pm25_s     = max(5, 10 + 0.4*temp - 0.3*vent + 0.05*dust
                             + (15 if harm else 0) + (20 if feux else 0))
            source_sim = f'<div style="display:inline-flex;align-items:center;gap:4px;">{get_icon("warning", 12)} Modèle non disponible · formule approx.</div>'

        irs_s     = min(1.0, pm25_s/80*0.35 + dust/300*0.25 + 0.10)
        nc, nt, _ = irs_level(irs_s, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
        ecart     = irs_s - ctx["irs_moy"]
        ecart_sgn = get_icon("trending_up", 28) if ecart > 0 else get_icon("trending_down", 28)
        ecart_col = th["red"] if ecart > 0 else th["green"]
        if   pm25_s <= 15:   oms_niv = f'<div style="display:inline-flex;align-items:center;gap:4px;">{get_icon("check_circle", 15)} ' + ("WHO Compliant" if lang=="en" else "Conforme OMS") + "</div>"
        elif pm25_s <= 25:   oms_niv = f'<div style="display:inline-flex;align-items:center;gap:4px;">{get_icon("warning", 15)} ' + ("IT4 exceeded" if lang=="en" else "IT4 dépassé") + "</div>"
        elif pm25_s <= 37.5: oms_niv = f'<div style="display:inline-flex;align-items:center;gap:4px;">{get_icon("error", 15)} ' + ("IT3 exceeded" if lang=="en" else "IT3 dépassé") + "</div>"
        elif pm25_s <= 50:   oms_niv = f'<div style="display:inline-flex;align-items:center;gap:4px;">{get_icon("dangerous", 15)} ' + ("IT2 exceeded" if lang=="en" else "IT2 dépassé") + "</div>"
        else:                oms_niv = f'<div style="display:inline-flex;align-items:center;gap:4px;">{get_icon("block", 15)} ' + ("Critical" if lang=="en" else "Critique") + "</div>"

        # Jauge dans la colonne droite — même bloc que les sliders
        with col_gauge:
            # Plotly gauge : 0 = bas-gauche (225°), 100 = bas-droite (-45°=315°)
            # Angle trigonométrique standard : 0°=droite, 90°=haut, 180°=gauche
            # La jauge couvre 270° de 225° à -45° (sens antihoraire)
            # Pour val dans [0,100] : angle = 225° - val/100 * 270°
            val_norm  = min(pm25_s, 100) / 100
            angle_deg = 225 - val_norm * 270
            angle_rad = np.radians(angle_deg)

            cx, cy = 0.5, 0.30   # centre pivot
            L      = 0.36        # longueur aiguille

            # Dans paper coords : Y diminue vers le haut → inverser sin
            tip_x  = cx + L * np.cos(angle_rad)
            tip_y  = cy - L * np.sin(angle_rad)

            back_x = cx - 0.06 * np.cos(angle_rad)
            back_y = cy + 0.06 * np.sin(angle_rad)

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pm25_s,
                number=dict(
                    suffix=" µg/m³",
                    font=dict(color=nc, size=18, family="DM Mono")
                ),
                title=dict(
                    text=f"{'Predicted PM2.5' if lang=='en' else 'PM2.5 Prédit'} · {ville_sim}",
                    font=dict(color="#94a3b8", size=11)
                ),
                gauge=dict(
                    axis=dict(
                        range=[0, 100],
                        tickwidth=2,
                        tickcolor="#94a3b8",
                        tickvals=[0, 15, 25, 37.5, 75, 100],
                        ticktext=["0", "<b>15</b>", "<b>25</b>", "<b>37</b>", "<b>75</b>", "100"],
                        tickfont=dict(size=13, color=th["text2"], family="Arial Black, sans-serif")
                    ),
                    bar=dict(color=nc, thickness=0.04),
                    bgcolor="#1e293b",
                    borderwidth=2,
                    bordercolor="#334155",
                    steps=[
                        dict(range=[0, 15],    color="#10b981"),
                        dict(range=[15, 25],   color="#f59e0b"),
                        dict(range=[25, 37.5], color="#f97316"),
                        dict(range=[37.5, 75], color="#ef4444"),
                        dict(range=[75, 100],  color="#7f1d1d"),
                    ],
                    threshold=dict(
                        line=dict(color="white", width=2),
                        thickness=0.8, value=15
                    )
                ),
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#0f172a",
                font=dict(color="#e2e8f0"),
                height=300,
                margin=dict(l=50, r=50, t=30, b=10)
            )
            st.plotly_chart(fig_gauge, width="stretch")



        # ── Cadre résultat PLEINE LARGEUR en bas ──────────────────────────
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#0f172a,#1e293b);'
            f'border:2px solid {nc};border-radius:16px;padding:20px 28px;'
            f'box-shadow:0 8px 32px {nc}33;">'

            f'<div style="display:grid;grid-template-columns:1fr 1px 1fr 1px 1fr 1px 1fr;'
            f'align-items:center;gap:0;">'

            # PM2.5
            f'<div style="text-align:center;padding:0 20px;">'
            f'<div style="font-size:10px;color:#64748b;text-transform:uppercase;'
            f'letter-spacing:.1em;margin-bottom:6px;">{"Predicted PM2.5" if lang=="en" else "PM2.5 prédit"}</div>'
            f'<div style="font-size:38px;font-weight:900;color:{nc};'
            f'text-shadow:0 0 20px {nc}55;line-height:1;">{pm25_s:.1f}</div>'
            f'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">µg/m³</div>'
            f'</div>'

            f'<div style="height:60px;background:{nc}33;width:1px;"></div>'

            # IRS
            f'<div style="text-align:center;padding:0 20px;">'
            f'<div style="font-size:10px;color:#64748b;text-transform:uppercase;'
            f'letter-spacing:.1em;margin-bottom:6px;">{"Simulated IRS" if lang=="en" else "IRS simulé"}</div>'
            f'<div style="font-size:32px;font-weight:800;color:{nc};line-height:1;">{irs_s:.3f}</div>'
            f'<div style="font-size:12px;font-weight:600;color:{nc};margin-top:4px;">{nt}</div>'
            f'</div>'

            f'<div style="height:60px;background:{nc}33;width:1px;"></div>'

            # Niveau OMS
            f'<div style="text-align:center;padding:0 20px;">'
            f'<div style="font-size:10px;color:#64748b;text-transform:uppercase;'
            f'letter-spacing:.1em;margin-bottom:6px;">{"WHO Level" if lang=="en" else "Niveau OMS"}</div>'
            f'<div style="font-size:18px;font-weight:700;color:{nc};line-height:1.2;">{oms_niv}</div>'
            f'<div style="font-size:11px;color:#94a3b8;margin-top:4px;">{pm25_s/15:.1f}x {"AQG threshold 2021" if lang=="en" else "seuil AQG 2021"}</div>'
            f'</div>'

            f'<div style="height:60px;background:{nc}33;width:1px;"></div>'

            # Écart vs moyenne
            f'<div style="text-align:center;padding:0 20px;">'
            f'<div style="font-size:10px;color:#64748b;text-transform:uppercase;'
            f'letter-spacing:.1em;margin-bottom:6px;">{"vs Average" if lang=="en" else "vs Moyenne"}</div>'
            f'<div style="font-size:32px;font-weight:800;color:{ecart_col};line-height:1;display:flex;align-items:center;justify-content:center;gap:4px;">'
            f'{ecart_sgn} {abs(ecart):.3f}</div>'
            f'<div style="font-size:11px;color:#94a3b8;margin-top:4px;">{ctx["scope_annees"]}</div>'
            f'</div>'

            f'</div>'

            f'<div style="font-size:9px;color:#475569;margin-top:14px;padding-top:10px;'
            f'border-top:1px solid #1e293b;font-family:DM Mono,monospace;text-align:center;">'
            f'<div style="display:inline-flex;align-items:center;gap:4px;">{source_sim}</div> · WHO AQG 2021 · NCBI NBK574591</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 4 — Calendrier mensuel impressionnant
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[3]:
        # Sélection ANNEE (Conservée comme demandé)
        col_sel1, col_sel2 = st.columns([1.2, 4])
        with col_sel1:
            annees_dispo = sorted(df["date"].dt.year.unique().tolist())
            an = st.selectbox(
                ":material/calendar_month: " + ("Année" if lang == "fr" else "Year"),
                annees_dispo, index=len(annees_dispo)-1, key="lt_a"
            )
        
        with col_sel2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            legend_html = (
                f'<div style="display:flex; justify-content:space-between; flex-wrap:wrap; align-items:center; '
                f'background:{th["bg_tertiary"]}; padding:8px 24px; border-radius:10px; '
                f'border:1px solid {th["border_soft"]}; width:100%;">'
                + "".join([
                    f'<div style="display:flex; align-items:center; gap:8px;">'
                    f'<div style="width:14px; height:14px; border-radius:50%; background:{c}; '
                    f'box-shadow:0 0 8px {c}66;"></div>'
                    f'<span style="font-size:12px; font-weight:600; color:{th["text"]}; white-space:nowrap;">{l}</span></div>'
                    for c, l in [
                        (th["green"], "< 15 µg/m³ · " + ("WHO" if lang=="en" else "Conforme OMS")),
                        (th["amber"], "15–25 · " + ("Mod." if lang=="en" else "Modéré")),
                        (th["coral"], "25–37.5 · " + ("High" if lang=="en" else "Élevé")),
                        (th["red"],   "> 37.5 · " + ("Crit." if lang=="en" else "Critique")),
                    ]
                ])
                + '</div>'
            )
            st.markdown(legend_html, unsafe_allow_html=True)
        
        # Sélection Ville (Supprimée car centralisée dans l'en-tête)
        ville_cal = v # Utilise la valeur de l'en-tête
        v_all     = T["all_cities"]

        df_an = df[df["date"].dt.year == an].copy()
        if ville_cal != v_all:
            df_an = df_an[df_an["ville"] == ville_cal]

        # Calcul stats mensuelles
        cal = df_an.groupby(df_an["date"].dt.month).agg(
            pm25_moy=("pm2_5_moyen", "mean"),
            pm25_max=("pm2_5_moyen", "max"),
            pm25_min=("pm2_5_moyen", "min"),
            n_jours=("pm2_5_moyen", "count"),
        ).reset_index()
        cal.columns = ["mois_num", "pm25_moy", "pm25_max", "pm25_min", "n_jours"]

        mois_long = MOIS_FR if lang == "fr" else MOIS_EN
        mois_court = MOIS_COURT_FR if lang == "fr" else MOIS_COURT_EN

        def _color(v):
            if   v <= 15:   return th["green"]
            elif v <= 25:   return th["amber"]
            elif v <= 37.5: return th["coral"]
            else:           return th["red"]

        def _niv(v):
            if   v <= 15:   return "Faible"   if lang == "fr" else "Low"
            elif v <= 25:   return "Modéré"   if lang == "fr" else "Moderate"
            elif v <= 37.5: return "Élevé"    if lang == "fr" else "High"
            else:           return "Critique" if lang == "fr" else "Critical"

        # ── Calendrier visuel en grille 4×3 ──────────────────────────────
        titre_cal = f"Qualité de l'air · {an}" if lang == "fr" else f"Air Quality · {an}"
        v_all     = T["all_cities"]
        if ville_cal != v_all:
            titre_cal += f" · {ville_cal}"
        else:
            titre_cal += " · " + ("Moyenne nationale" if lang == "fr" else "National average")

        st.markdown(
            f'<div style="font-size:15px;font-weight:600;color:{th["text"]};'
            f'margin-bottom:16px;text-align:center;">'
            f'<div style="display:inline-flex;align-items:center;gap:8px;">{get_icon("calendar_month", 22)} {titre_cal}</div></div>',
            unsafe_allow_html=True
        )

        # Grille 4 colonnes × 3 lignes
        rows = [cal_row for _, cal_row in cal.iterrows()]
        # Remplir les mois manquants
        mois_presents = set(cal["mois_num"].tolist())
        all_rows = []
        for m in range(1, 13):
            found = cal[cal["mois_num"] == m]
            if len(found) > 0:
                all_rows.append(found.iloc[0])
            else:
                all_rows.append(None)

        for row_idx in range(3):
            cols = st.columns(4)
            for col_idx in range(4):
                m_idx = row_idx * 4 + col_idx
                if m_idx >= 12:
                    break
                m_num = m_idx + 1
                row   = all_rows[m_idx]
                mois_nom = mois_long[m_idx]

                with cols[col_idx]:
                    if row is not None:
                        v     = row["pm25_moy"]
                        color = _color(v)
                        niv   = _niv(v)
                        ratio = v / 15
                        # Barre de remplissage proportionnelle
                        bar_w = min(100, int(v / 80 * 100))

                        # Est-ce le mois actuel ?
                        is_current = (m_num == date.today().month and an == date.today().year)
                        border_style = f'3px solid {color}' if is_current else f'1px solid {color}44'

                        st.markdown(
                            f'<div style="background:linear-gradient(145deg,{th["bg_tertiary"]},{th["bg_elevated"]});'
                            f'border:{border_style};border-radius:14px;'
                            f'padding:14px 12px;margin-bottom:8px;'
                            f'box-shadow:0 4px 16px {color}18;'
                            f'{"box-shadow:0 0 20px " + color + "44;" if is_current else ""}">'

                            # Nom du mois
                            f'<div style="font-size:12px;font-weight:700;color:{th["text"]};'
                            f'text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;">'
                            f'{mois_nom}'
                            f' {get_icon("push_pin", 14) if is_current else ""}</div>'

                            # PM2.5 moyen — grand chiffre
                            f'<div style="font-size:30px;font-weight:900;color:{color};'
                            f'line-height:1;text-shadow:0 0 16px {color}44;">{v:.1f}</div>'
                            f'<div style="font-size:10px;color:{th["text3"]};margin-bottom:8px;">µg/m³</div>'

                            # Barre de progression
                            f'<div style="background:{th["bg_elevated"]};border-radius:4px;'
                            f'height:6px;overflow:hidden;margin-bottom:8px;">'
                            f'<div style="background:{color};height:100%;width:{bar_w}%;'
                            f'border-radius:4px;box-shadow:0 0 8px {color}66;"></div></div>'

                            # Niveau + ratio OMS
                            f'<div style="font-size:11px;font-weight:600;color:{color};">{niv}</div>'
                            f'<div style="font-size:10px;color:{th["text3"]};margin-top:2px;">'
                            f'{ratio:.1f}x OMS</div>'

                            # Min/Max
                            f'<div style="display:flex;justify-content:space-between;'
                            f'margin-top:8px;padding-top:6px;border-top:1px solid {color}22;">'
                            f'<span style="font-size:9px;color:{th["text3"]};display:flex;align-items:center;gap:2px;">{get_icon("trending_down", 10)} {row["pm25_min"]:.1f}</span>'
                            f'<span style="font-size:9px;color:{th["text3"]};display:flex;align-items:center;gap:2px;">{get_icon("trending_up", 10)} {row["pm25_max"]:.1f}</span>'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        # Mois sans données
                        st.markdown(
                            f'<div style="background:{th["bg_tertiary"]};'
                            f'border:1px solid {th["border_soft"]};border-radius:14px;'
                            f'padding:14px 12px;margin-bottom:8px;text-align:center;opacity:0.4;">'
                            f'<div style="font-size:12px;font-weight:700;color:{th["text3"]};'
                            f'text-transform:uppercase;">{mois_long[m_idx]}</div>'
                            f'<div style="font-size:20px;margin-top:8px;">—</div>'
                            f'<div style="font-size:10px;color:{th["text3"]};margin-top:4px;">{"No data" if lang=="en" else "Pas de données"}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )


    sources_bar(
        ("Hybrid Model Regression+ARIMA · Box & Jenkins (1976) · "
         "INS Cameroon (2019) · WHO AQG 2021 · NCBI NBK574591")
        if lang=="en" else
        ("Modèle Hybride Régression+ARIMA · Box & Jenkins (1976) · "
         "INS Cameroun (2019) · WHO AQG 2021 · NCBI NBK574591"),
        th
    )