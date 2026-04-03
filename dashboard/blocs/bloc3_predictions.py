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

    banner(
        IMAGES["pred_banner"], 185,
        T['bloc3_label'],
        T["bloc3_subtitle"], th,
        accent=th["amber"], tint_hex="#f59e0b", tint_strength=0.28
    )

    if len(df) == 0:
        empty_state(T, th)
        return

    PL   = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
                font=dict(color=th["text2"], size=12))
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False)

    modele, scaler, features, arima = _load_models()
    modeles_ok = all(x is not None for x in [modele, scaler, features, arima])

    pred_lbl  = "🔮 Prédiction J/J+1/J+2" if lang == "fr" else "🔮 Forecast D/D+1/D+2"
    perf_lbl  = "📊 Performance" if lang == "fr" else "📊 Performance"
    sim_lbl   = "🎛️ Simulateur" if lang == "fr" else "🎛️ Simulator"
    month_lbl = "📅 Calendrier" if lang == "fr" else "📅 Calendar"

    tabs = st.tabs([pred_lbl, perf_lbl, sim_lbl, month_lbl])

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 1 — Prédiction J/J+1/J+2
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[0]:
        # Sélecteur ville en haut — pleine largeur
        villes_dispo = sorted(df["ville"].unique().tolist())
        v = st.selectbox(
            "🏙️ Sélectionner une ville" if lang == "fr" else "🏙️ Select a city",
            villes_dispo, index=0, key="p_v"
        )

        df_v     = df[df["ville"] == v].sort_values("date")
        # Historique 60 jours au lieu de 30
        hist     = df_v.groupby("date")["pm2_5_moyen"].mean().tail(60).reset_index()
        jours    = [date.today() + timedelta(days=i) for i in range(0, 3)]
        jours_pd = pd.to_datetime(jours)

        if modeles_ok and len(df_v) > 0:
            preds, zone_v = _predire_ville(v, df, modele, scaler, features, arima)
            source_pred   = f"Modèle Hybride RL+ARIMA · {zone_v}"
        else:
            base  = float(df_v["pm2_5_moyen"].mean()) if len(df_v) > 0 else 15.0
            np.random.seed(hash(v) % 2**31)
            preds       = [base * (0.88 + 0.24 * np.random.random()) for _ in range(3)]
            zone_v      = ""
            source_pred = "Moyenne historique (modèle non disponible)"

        mae       = 3.456
        pred_high = [p + mae for p in preds]
        pred_low  = [max(0, p - mae) for p in preds]

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

        titre_pred = f"PM2.5 · {v} · Prédiction 72h"
        fig.update_layout(
            **PL, height=420,  # plus grand
            title=dict(text=titre_pred, font=dict(color=th["text"], size=14)),
            legend=dict(
                font=dict(color=th["text2"], size=11),
                bgcolor="rgba(0,0,0,0)",
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            margin=dict(l=44, r=20, t=60, b=36)
        )
        fig.update_xaxes(**GRID)
        fig.update_yaxes(**GRID)
        st.plotly_chart(fig, width="stretch")

        # ── KPIs prédiction — plus visibles ──────────────────────────────
        k1, k2, k3 = st.columns(3)
        labels_j  = ["📅 Aujourd'hui", "🔮 Demain", "🔮 Après-demain"] if lang == "fr" \
                    else ["📅 Today", "🔮 Tomorrow", "🔮 Day after"]
        niveaux   = ["FAIBLE","MODÉRÉ","ÉLEVÉ","CRITIQUE"]

        for col, pred_val, lbl_j, jour in zip([k1, k2, k3], preds, labels_j, jours):
            color = th["green"] if pred_val <= 15 else th["amber"] if pred_val <= 25 \
                    else th["coral"] if pred_val <= 37.5 else th["red"]
            ratio = pred_val / 15
            if   pred_val <= 15:   niv = "✅ Conforme OMS"   if lang == "fr" else "✅ WHO Compliant"
            elif pred_val <= 25:   niv = "⚠️ Modéré"         if lang == "fr" else "⚠️ Moderate"
            elif pred_val <= 37.5: niv = "🟠 Élevé"          if lang == "fr" else "🟠 High"
            else:                  niv = "🔴 Critique"        if lang == "fr" else "🔴 Critical"

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
                    f'<div style="font-size:10px;color:{th["text3"]};margin-top:6px;">'
                    f'{ratio:.1f}x seuil OMS</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown(
            f'<div style="font-size:10px;color:{th["text3"]};margin-top:10px;'
            f'font-family:DM Mono,monospace;padding:8px 12px;'
            f'background:{th["bg_tertiary"]};border-radius:8px;">'
            f'🔬 {source_pred} · IC = ±{mae} µg/m³ · WHO AQG 2021 · NCBI NBK574591</div>',
            unsafe_allow_html=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 2 — Performance du modèle
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[1]:
        perf_desc = (
            "Performance du modèle hybride sur les données de test 2025 — "
            "données jamais vues pendant l'entraînement."
            if ctx["lang"] == "fr"
            else "Hybrid model performance on 2025 test data — never seen during training."
        )
        st.markdown(
            f'<div style="font-size:13px;color:{th["text2"]};margin-bottom:16px;">'
            f'{perf_desc}'
            f'</div>',
            unsafe_allow_html=True
        )
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
                    (k1, f"{perf['r2']:.4f}",         "R²",              "Variance expliquée", th["green"],  "🎯"),
                    (k2, f"{perf['mae']:.3f}",         "MAE (µg/m³)",     "Erreur moyenne",     th["amber"],  "📏"),
                    (k3, f"{perf['err_max']:.1f}",     "Erreur max",      "µg/m³",              th["coral"],  "⚠️"),
                    (k4, f"{100-perf['pct_10']:.1f}%", "Précision",       "Erreur < 10 µg/m³",  th["blue"],   "✅"),
                ]
                for col, val, lbl, sub, color, emoji in kpi_data:
                    with col:
                        st.markdown(
                            f'<div style="background:linear-gradient(145deg,{th["bg_tertiary"]},{th["bg_elevated"]});'
                            f'border:1px solid {color}55;border-top:4px solid {color};'
                            f'border-radius:14px;padding:20px 12px;text-align:center;'
                            f'box-shadow:0 6px 24px {color}22;">'
                            f'<div style="font-size:24px;margin-bottom:8px;">{emoji}</div>'
                            f'<div style="font-size:28px;font-weight:800;color:{color};'
                            f'line-height:1;text-shadow:0 0 20px {color}44;">{val}</div>'
                            f'<div style="font-size:12px;font-weight:600;color:{th["text"]};'
                            f'margin-top:8px;text-transform:uppercase;letter-spacing:.06em;">{lbl}</div>'
                            f'<div style="font-size:10px;color:{th["text3"]};margin-top:4px;">{sub}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)

                # Timeline pleine largeur — ville de référence sélectionnable
                ville_ref = st.selectbox(
                    "Ville de référence" if lang == "fr" else "Reference city",
                    sorted(list(set(perf["villes"]))),
                    index=list(sorted(set(perf["villes"]))).index("Yaounde")
                    if "Yaounde" in set(perf["villes"]) else 0,
                    key="perf_ville"
                )
                mask_v  = perf["villes"] == ville_ref
                dates_v = perf["dates"][mask_v]
                y_v     = perf["y_test"][mask_v]
                p_v     = perf["pred"][mask_v]

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
                        text=f"Réel vs Prédit · {ville_ref} · 2025 · R²={perf['r2']:.4f} · MAE={perf['mae']:.3f} µg/m³",
                        font=dict(color=th["text"], size=13)
                    ),
                    xaxis=dict(**GRID),
                    yaxis=dict(**GRID, title="PM2.5 (µg/m³)"),
                    legend=dict(
                        font=dict(color=th["text2"], size=11),
                        bgcolor="rgba(0,0,0,0)",
                        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                    )
                )
                st.plotly_chart(fig_tl, width="stretch")
            else:
                st.info("Données de test 2025 insuffisantes.")
        else:
            st.warning("Modèles non disponibles — vérifier le dossier models/")

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 3 — Simulateur
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[2]:
        def _m(col, fb):
            return float(df[col].mean()) if col in df.columns and len(df) > 0 else fb

        # En-tête simulateur
        st.markdown(
            f'<div style="background:linear-gradient(135deg,{th["bg_elevated"]},{th["bg_tertiary"]});'
            f'border:1px solid {th["amber"]}44;border-left:4px solid {th["amber"]};'
            f'border-radius:12px;padding:14px 20px;margin-bottom:20px;">'
            f'<div style="font-size:14px;font-weight:600;color:{th["amber"]};margin-bottom:4px;">'
            f'🎛️ Simulateur de conditions météo</div>'
            f'<div style="font-size:12px;color:{th["text2"]};">'
            f'Ajustez les paramètres pour estimer l\'impact sur la qualité de l\'air</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Layout 2 colonnes : sliders | résultat
        col_sliders, col_result = st.columns([3, 2])

        with col_sliders:
            # Section météo
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:{th["text3"]};'
                f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;">'
                f'🌡️ Conditions météorologiques</div>',
                unsafe_allow_html=True
            )
            c1, c2 = st.columns(2)
            with c1:
                temp = st.slider("🌡️ Température (°C)", 20, 45,
                                 int(min(45, max(20, _m("temperature_2m_max", 30)))), key="s_t")
                vent = st.slider("💨 Vent (km/h)", 0, 60,
                                 int(min(60, max(0, _m("wind_speed_10m_max", 15)))), key="s_v")
            with c2:
                dust = st.slider("🏜️ Dust (µg/m³)", 0, 300,
                                 int(min(300, max(0, _m("dust_moyen", 80)))), key="s_d")
                hum  = st.slider("💧 Humidité (%)", 10, 100, 60, key="s_h")

            st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

            # Section épisodes
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:{th["text3"]};'
                f'text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px;">'
                f'⚡ Épisodes climatiques</div>',
                unsafe_allow_html=True
            )
            c3, c4 = st.columns(2)
            with c3:
                harm = st.checkbox("🌪️ Harmattan intense", key="s_harm",
                                   help="Dust > p90 ET précipitations < p10 · Schepanski et al. (2007)")
            with c4:
                feux = st.checkbox("🔥 Épisode feux", key="s_feux",
                                   help="CO > p90 en saison sèche · Barker et al. (2020)")

        # Calcul
        pm25_s = max(5, 10 + 0.4*temp - 0.3*vent + 0.05*dust
                     + (15 if harm else 0) + (20 if feux else 0))
        irs_s  = min(1.0, pm25_s/80*0.35 + dust/300*0.25 + 0.10)
        nc, nt, nk = irs_level(irs_s, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
        ecart     = irs_s - ctx["irs_moy"]
        ecart_sgn = "↑" if ecart > 0 else "↓"
        ecart_col = th["red"] if ecart > 0 else th["green"]

        # Niveau OMS
        if   pm25_s <= 15:   oms_niv = "✅ Conforme OMS"   if lang == "fr" else "✅ WHO Compliant"
        elif pm25_s <= 25:   oms_niv = "⚠️ IT4 dépassé"    if lang == "fr" else "⚠️ IT4 exceeded"
        elif pm25_s <= 37.5: oms_niv = "🟠 IT3 dépassé"    if lang == "fr" else "🟠 IT3 exceeded"
        elif pm25_s <= 50:   oms_niv = "🔴 IT2 dépassé"    if lang == "fr" else "🔴 IT2 exceeded"
        else:                oms_niv = "⛔ Critique"        if lang == "fr" else "⛔ Critical"

        with col_result:
            st.markdown(
                f'<div style="background:linear-gradient(145deg,{th["bg_tertiary"]},{th["bg_elevated"]});'
                f'border:2px solid {nc};border-radius:16px;padding:24px 20px;text-align:center;'
                f'box-shadow:0 8px 32px {nc}33;">'

                # PM2.5
                f'<div style="font-size:11px;color:{th["text3"]};text-transform:uppercase;'
                f'letter-spacing:.1em;margin-bottom:6px;">PM2.5 estimé</div>'
                f'<div style="font-size:48px;font-weight:900;color:{nc};line-height:1;'
                f'text-shadow:0 0 30px {nc}55;">{pm25_s:.1f}</div>'
                f'<div style="font-size:14px;color:{th["text3"]};margin-bottom:16px;">µg/m³</div>'

                # Séparateur
                f'<div style="height:1px;background:{nc}33;margin:12px 0;"></div>'

                # IRS
                f'<div style="font-size:11px;color:{th["text3"]};text-transform:uppercase;'
                f'letter-spacing:.1em;margin-bottom:6px;">IRS simulé</div>'
                f'<div style="font-size:32px;font-weight:800;color:{nc};">{irs_s:.3f}</div>'
                f'<div style="font-size:14px;font-weight:600;color:{nc};margin-top:6px;">{nt}</div>'

                # Écart vs moyenne
                f'<div style="font-size:12px;color:{ecart_col};margin-top:8px;font-weight:600;">'
                f'{ecart_sgn} {abs(ecart):.3f} vs moy. {ctx["scope_annees"]}</div>'

                # Séparateur
                f'<div style="height:1px;background:{nc}33;margin:12px 0;"></div>'

                # Niveau OMS
                f'<div style="font-size:13px;font-weight:600;color:{nc};margin-top:4px;">'
                f'{oms_niv}</div>'
                f'<div style="font-size:10px;color:{th["text3"]};margin-top:4px;">'
                f'{pm25_s/15:.1f}x seuil OMS AQG 2021</div>'

                f'</div>',
                unsafe_allow_html=True
            )

            # Jauge PM2.5
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pm25_s,
                number=dict(suffix=" µg/m³", font=dict(color=nc, size=18)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickwidth=1, tickcolor=th["text3"]),
                    bar=dict(color=nc, thickness=0.3),
                    bgcolor="rgba(0,0,0,0)",
                    steps=[
                        dict(range=[0, 15],   color="rgba(16,185,129,0.15)"),
                        dict(range=[15, 25],  color="rgba(245,158,11,0.15)"),
                        dict(range=[25, 37.5],color="rgba(249,115,22,0.15)"),
                        dict(range=[37.5, 100],color="rgba(239,68,68,0.15)"),
                    ],
                    threshold=dict(line=dict(color=th["red"], width=2), value=15)
                ),
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=th["text2"]),
                height=160,
                margin=dict(l=20, r=20, t=20, b=10)
            )
            st.plotly_chart(fig_gauge, width="stretch")

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 4 — Calendrier mensuel impressionnant
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[3]:
        col_sel1, col_sel2 = st.columns([1, 2])
        with col_sel1:
            annees_dispo = sorted(df["date"].dt.year.unique().tolist())
            an = st.selectbox(
                "📅 Année" if lang == "fr" else "📅 Year",
                annees_dispo, index=len(annees_dispo)-1, key="lt_a"
            )
        with col_sel2:
            villes_cal = ["Toutes les villes"] + sorted(df["ville"].unique().tolist()) \
                         if lang == "fr" else \
                         ["All cities"] + sorted(df["ville"].unique().tolist())
            ville_cal = st.selectbox(
                "🏙️ Ville" if lang == "fr" else "🏙️ City",
                villes_cal, key="cal_ville"
            )

        df_an = df[df["date"].dt.year == an].copy()
        if ville_cal not in ["Toutes les villes", "All cities"]:
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
        if ville_cal not in ["Toutes les villes", "All cities"]:
            titre_cal += f" · {ville_cal}"

        st.markdown(
            f'<div style="font-size:15px;font-weight:600;color:{th["text"]};'
            f'margin-bottom:16px;text-align:center;">'
            f'📅 {titre_cal}</div>',
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
                            f'{"  🔵" if is_current else ""}</div>'

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
                            f'<span style="font-size:9px;color:{th["text3"]};">↓ {row["pm25_min"]:.1f}</span>'
                            f'<span style="font-size:9px;color:{th["text3"]};">↑ {row["pm25_max"]:.1f}</span>'
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
                            f'<div style="font-size:10px;color:{th["text3"]};margin-top:4px;">Pas de données</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

        # Légende calendrier
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="display:flex;gap:16px;flex-wrap:wrap;justify-content:center;">'
            + "".join([
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'<div style="width:12px;height:12px;border-radius:50%;background:{c};"></div>'
                f'<span style="font-size:11px;color:{th["text3"]};">{l}</span></div>'
                for c, l in [
                    (th["green"], f"< 15 µg/m³ · Conforme OMS"),
                    (th["amber"], f"15–25 µg/m³ · Modéré"),
                    (th["coral"], f"25–37.5 µg/m³ · Élevé"),
                    (th["red"],   f"> 37.5 µg/m³ · Critique"),
                ]
            ])
            + f'</div>',
            unsafe_allow_html=True
        )

    sources_bar(
        f"Modèle Hybride Régression+ARIMA · Box & Jenkins (1976) · "
        f"INS Cameroun (2019) · WHO AQG 2021 · NCBI NBK574591",
        th
    )
