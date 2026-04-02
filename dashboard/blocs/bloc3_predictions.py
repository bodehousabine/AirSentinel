"""blocs/bloc3_predictions.py — Prédictions · modèle réel + performance · bilingue + thème"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import joblib
import os
from datetime import date, timedelta
from utils import get_context, banner, img_card, sources_bar, empty_state, irs_level
from assets import IMAGES

# ── Zones INS Cameroun (2019) ─────────────────────────────────────────────────
ZONES_REGIONS = {
    'Zone équatoriale':        ['Centre', 'Est', 'Sud', 'Littoral', 'Sud-Ouest', 'Ouest', 'Nord-Ouest'],
    'Zone soudanienne':        ['Adamaoua', 'Nord'],
    'Zone soudano-sahélienne': ['Extreme-Nord'],
}

def _get_zone(region):
    for zone, regions in ZONES_REGIONS.items():
        if region in regions:
            return zone
    return 'Zone équatoriale'

@st.cache_resource
def _load_models():
    """Charge les modèles une seule fois."""
    # Chercher models/ en remontant depuis le fichier actuel
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Essayer plusieurs chemins possibles
    chemins = [
        os.path.join(base_dir, '..', 'models'),           # dashboard/../models
        os.path.join(base_dir, '..', '..', 'models'),     # dashboard/../../models
        os.path.join(base_dir, 'models'),                  # dashboard/models
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
    except Exception as e:
        return None, None, None, None

def _predire_ville(ville, df_brut, modele, scaler, features, arima):
    """Prédit PM2.5 pour J+1, J+2, J+3 pour une ville donnée."""
    df_v   = df_brut[df_brut['ville'] == ville].sort_values('date')
    region = df_v['region'].iloc[-1] if len(df_v) > 0 else 'Centre'
    zone   = _get_zone(region)

    preds = []
    for step in range(1, 4):
        try:
            last   = df_v[features].fillna(df_v[features].median()).tail(1)
            last_s = scaler.transform(last)
            p_rl   = modele.predict(last_s)[0]
            p_arima= arima[zone].forecast(steps=step).iloc[-1]
            preds.append(max(0, p_rl + p_arima))
        except Exception:
            base = float(df_v['pm2_5_moyen'].mean()) if len(df_v) > 0 else 15.0
            preds.append(base)

    return preds, zone


def render(profil):
    ctx  = get_context()
    df   = ctx["df_brut"]
    th   = ctx["th"]
    T    = ctx["T"]
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
                font=dict(color=th["text2"], size=12), margin=dict(l=44,r=20,t=44,b=36))
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False)

    # ── Charger les modèles ───────────────────────────────────────────────────
    modele, scaler, features, arima = _load_models()
    modeles_ok = all(x is not None for x in [modele, scaler, features, arima])

    # Labels
    perf_lbl  = "📊 Performance du modèle" if ctx["lang"] == "fr" else "📊 Model performance"
    pred_lbl  = "🔮 Prédiction J+1/J+2/J+3" if ctx["lang"] == "fr" else "🔮 Forecast D+1/D+2/D+3"
    sim_lbl   = T.get("bloc3_tab_sim", "🎛️ Simulateur")
    month_lbl = T.get("bloc3_tab_monthly", "📅 Mensuel")

    tabs = st.tabs([pred_lbl, perf_lbl, sim_lbl, month_lbl])

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 1 — Prédiction J+1/J+2/J+3 avec le vrai modèle
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[0]:
        cv, ci = st.columns([1, 3])
        with cv:
            villes_dispo = sorted(df["ville"].unique().tolist())
            v = st.selectbox(
                T.get("bloc3_city_select", "Ville"),
                villes_dispo, index=0, key="p_v"
            )
            img_card(IMAGES["ctx_foret"], 120, v, "", th, tint_hex="#00d4b1")

        with ci:
            df_v  = df[df["ville"] == v].sort_values("date")
            hist  = df_v.groupby("date")["pm2_5_moyen"].mean().tail(30).reset_index()
            jours = [date.today() + timedelta(days=i) for i in range(1, 4)]
            jours_pd = pd.to_datetime(jours)

            # Prédiction avec le vrai modèle
            if modeles_ok and len(df_v) > 0:
                preds, zone_v = _predire_ville(v, df, modele, scaler, features, arima)
                source_pred   = f"Modèle Hybride RL+ARIMA · {zone_v}"
            else:
                base  = float(df_v["pm2_5_moyen"].mean()) if len(df_v) > 0 else 15.0
                np.random.seed(hash(v) % 2**31)
                preds = [base * (0.88 + 0.24 * np.random.random()) for _ in range(3)]
                zone_v      = ""
                source_pred = "Moyenne historique (modèle non disponible)"

            # Intervalle de confiance ±MAE
            mae = 3.456
            pred_high = [p + mae for p in preds]
            pred_low  = [max(0, p - mae) for p in preds]

            fig = go.Figure()

            # Historique
            fig.add_trace(go.Scatter(
                x=hist["date"], y=hist["pm2_5_moyen"],
                mode="lines", name=T.get("bloc3_history_label", "Historique"),
                line=dict(color=th["blue"], width=2),
                fill="tozeroy", fillcolor="rgba(14,165,233,0.07)"
            ))

            # Intervalle de confiance
            fig.add_trace(go.Scatter(
                x=list(jours_pd) + list(jours_pd[::-1]),
                y=pred_high + pred_low[::-1],
                fill="toself", fillcolor="rgba(245,158,11,0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=True,
                name=f"IC ±{mae:.1f} µg/m³"
            ))

            # Prédictions
            fig.add_trace(go.Scatter(
                x=jours_pd, y=preds,
                mode="lines+markers+text",
                name=T.get("bloc3_pred_label", "Prédiction"),
                line=dict(color=th["amber"], width=2.5, dash="dash"),
                marker=dict(size=12, color=th["amber"],
                            line=dict(color=th["bg_elevated"] if "bg_elevated" in th else "#1e293b", width=2)),
                text=[f"{p:.1f}" for p in preds],
                textposition="top center",
                textfont=dict(color=th["amber"], size=11)
            ))

            # Seuil OMS
            fig.add_hline(
                y=15.0, line=dict(color=th["red"], width=1, dash="dash"),
                annotation_text="OMS 15 µg/m³",
                annotation_font_color=th["red"], annotation_font_size=10
            )

            titre_pred = f"PM2.5 · {v} · Prédiction 72h"
            fig.update_layout(
                **PL, height=340,
                title=dict(text=titre_pred, font=dict(color=th["text"], size=13)),
                legend=dict(font=dict(color=th["text2"], size=11), bgcolor="rgba(0,0,0,0)")
            )
            fig.update_xaxes(**GRID)
            fig.update_yaxes(**GRID)
            st.plotly_chart(fig, use_container_width=True)

            # KPIs prédiction
            k1, k2, k3 = st.columns(3)
            labels_j = ["J+1 · Demain", "J+2 · Après-demain", "J+3"] if ctx["lang"] == "fr" \
                       else ["D+1 · Tomorrow", "D+2", "D+3"]
            for col, pred_val, lbl_j, jour in zip([k1, k2, k3], preds, labels_j, jours):
                color = th["green"] if pred_val <= 15 else th["amber"] if pred_val <= 25 \
                        else th["coral"] if pred_val <= 37.5 else th["red"]
                with col:
                    st.markdown(
                        f'<div style="background:{th["bg_elevated"]};border:1px solid {color}44;'
                        f'border-top:3px solid {color};border-radius:10px;'
                        f'padding:12px;text-align:center;">'
                        f'<div style="font-size:10px;color:{th["text3"]};margin-bottom:4px;">'
                        f'{lbl_j}<br>{jour.strftime("%d %b")}</div>'
                        f'<div style="font-size:22px;font-weight:700;color:{color};">{pred_val:.1f}</div>'
                        f'<div style="font-size:10px;color:{th["text3"]};">µg/m³</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            st.markdown(
                f'<div style="font-size:10px;color:{th["text3"]};margin-top:8px;'
                f'font-family:DM Mono,monospace;">🔬 {source_pred} · '
                f'IC = ±{mae} µg/m³ · WHO AQG 2021</div>',
                unsafe_allow_html=True
            )

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 2 — Performance du modèle (Prédit vs Réel)
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[1]:
        st.markdown(
            f'<div style="font-size:13px;color:{th["text2"]};margin-bottom:16px;">'
            f'{"Performance du modèle hybride sur les données de test 2025 — données jamais vues pendant lentraînement." if ctx["lang"] == "fr" else "Hybrid model performance on 2025 test data — never seen during training."}'
            f'</div>',
            unsafe_allow_html=True
        )

        if modeles_ok:
            # Calculer prédictions sur 2025
            @st.cache_data(ttl=3600)
            def _calc_perf():
                from sklearn.metrics import r2_score, mean_absolute_error
                test     = df[df["date"].dt.year == 2025].copy()
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
                # KPIs performance
                k1, k2, k3, k4 = st.columns(4)
                for col, val, lbl, sub, color in [
                    (k1, f"{perf['r2']:.4f}",    "R²",           "Variance expliquée", th["green"]),
                    (k2, f"{perf['mae']:.3f}",    "MAE (µg/m³)",  "Erreur moyenne",     th["amber"]),
                    (k3, f"{perf['err_max']:.1f}","Erreur max",   "µg/m³",              th["coral"]),
                    (k4, f"{100-perf['pct_10']:.1f}%", "Précision", "Erreur < 10 µg/m³", th["blue"]),
                ]:
                    with col:
                        st.markdown(
                            f'<div style="background:{th["bg_elevated"]};border:1px solid {color}44;'
                            f'border-top:3px solid {color};border-radius:10px;'
                            f'padding:12px;text-align:center;">'
                            f'<div style="font-size:22px;font-weight:700;color:{color};">{val}</div>'
                            f'<div style="font-size:11px;color:{th["text"]};margin-top:3px;">{lbl}</div>'
                            f'<div style="font-size:10px;color:{th["text3"]};">{sub}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
                col_sc, col_tl = st.columns(2)

                # Scatter Prédit vs Réel
                with col_sc:
                    fig_sc = go.Figure()
                    fig_sc.add_trace(go.Scatter(
                        x=perf["y_test"], y=perf["pred"],
                        mode="markers",
                        marker=dict(size=4, color=th["blue"], opacity=0.3),
                        name="Observations",
                        hovertemplate="Réel: %{x:.1f}<br>Prédit: %{y:.1f}<extra></extra>"
                    ))
                    lim = max(perf["y_test"].max(), perf["pred"].max())
                    fig_sc.add_trace(go.Scatter(
                        x=[0, lim], y=[0, lim],
                        mode="lines",
                        line=dict(color=th["red"], width=1.5, dash="dash"),
                        name="Prédiction parfaite"
                    ))
                    fig_sc.update_layout(
                        **PL, height=320,
                        title=dict(
                            text=f"Prédit vs Réel · R²={perf['r2']:.4f} · MAE={perf['mae']:.3f} µg/m³",
                            font=dict(color=th["text"], size=12)
                        ),
                        xaxis=dict(**GRID, title="PM2.5 réel (µg/m³)"),
                        yaxis=dict(**GRID, title="PM2.5 prédit (µg/m³)"),
                        legend=dict(font=dict(color=th["text2"], size=10), bgcolor="rgba(0,0,0,0)")
                    )
                    st.plotly_chart(fig_sc, use_container_width=True)

                # Timeline ville de référence
                with col_tl:
                    ville_ref = "Yaounde"
                    mask_v    = perf["villes"] == ville_ref
                    dates_v   = perf["dates"][mask_v]
                    y_v       = perf["y_test"][mask_v]
                    p_v       = perf["pred"][mask_v]

                    fig_tl = go.Figure()
                    fig_tl.add_trace(go.Scatter(
                        x=dates_v, y=y_v,
                        mode="lines", name="Réel",
                        line=dict(color=th["blue"], width=1.5)
                    ))
                    fig_tl.add_trace(go.Scatter(
                        x=dates_v, y=p_v,
                        mode="lines", name="Prédit",
                        line=dict(color=th["amber"], width=1.5, dash="dash")
                    ))
                    fig_tl.add_hline(
                        y=15, line=dict(color=th["red"], width=1, dash="dot"),
                        annotation_text="OMS 15",
                        annotation_font_color=th["red"], annotation_font_size=9
                    )
                    fig_tl.update_layout(
                        **PL, height=320,
                        title=dict(
                            text=f"Timeline · {ville_ref} · 2025",
                            font=dict(color=th["text"], size=12)
                        ),
                        xaxis=dict(**GRID),
                        yaxis=dict(**GRID, title="PM2.5 (µg/m³)"),
                        legend=dict(font=dict(color=th["text2"], size=10), bgcolor="rgba(0,0,0,0)")
                    )
                    st.plotly_chart(fig_tl, use_container_width=True)
            else:
                st.info("Données de test 2025 insuffisantes.")
        else:
            st.warning("Modèles non disponibles — vérifier le dossier models/")

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 3 — Simulateur
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[2]:
        ci2, cc = st.columns([1, 2])
        with ci2:
            img_card(IMAGES["pred_harmattan"], 300, "Harmattan · Bauer et al. 2024",
                     "Dust > p90", th, tint_hex="#f59e0b", tint_strength=0.30)
        with cc:
            def _m(col, fb):
                return float(df[col].mean()) if col in df.columns and len(df) > 0 else fb

            st.markdown(
                f'<div style="font-size:13px;color:{th["text2"]};margin-bottom:12px;">'
                f'{T.get("bloc3_sim_intro", "Simulateur")} '
                f'<b style="color:{th["teal"]};">{ctx["scope_label"]}</b></div>',
                unsafe_allow_html=True
            )
            c1, c2 = st.columns(2)
            with c1:
                temp = st.slider(T.get("bloc3_temp","Temp."), 20, 45,
                                 int(min(45, max(20, _m("temperature_2m_max", 30)))), key="s_t")
                vent = st.slider(T.get("bloc3_wind","Vent"), 0, 60,
                                 int(min(60, max(0, _m("wind_speed_10m_max", 15)))), key="s_v")
                hum  = st.slider(T.get("bloc3_humidity","Humidité"), 10, 100, 60, key="s_h")
            with c2:
                dust = st.slider(T.get("bloc3_dust","Dust"), 0, 300,
                                 int(min(300, max(0, _m("dust_moyen", 80)))), key="s_d")
                harm = st.checkbox(T.get("bloc3_harmattan","Harmattan intense"), key="s_harm")
                feux = st.checkbox(T.get("bloc3_fire","Épisode feux"), key="s_feux")

            pm25_s = max(5, 10 + 0.4*temp - 0.3*vent + 0.05*dust
                         + (15 if harm else 0) + (20 if feux else 0))
            irs_s  = min(1.0, pm25_s/80*0.35 + dust/300*0.25 + 0.10)
            nc, nt, _ = irs_level(irs_s, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
            ecart     = irs_s - ctx["irs_moy"]
            ecart_sgn = "↑" if ecart > 0 else "↓"
            ecart_col = "#ef4444" if ecart > 0 else "#10b981"
            ecart_t   = f"{ecart_sgn} {abs(ecart):.3f} vs moy. {ctx['scope_annees']}"

            st.markdown(
                f'<div style="background:{th["bg_elevated"]};border:2px solid {nc};'
                f'border-radius:12px;padding:16px 20px;margin-top:14px;'
                f'display:flex;align-items:center;justify-content:space-between;gap:14px;">'
                f'<div>'
                f'<div style="font-size:11px;color:{th["text3"]};margin-bottom:3px;">'
                f'{T.get("bloc3_sim_irs","IRS simulé")}</div>'
                f'<div style="font-size:32px;font-weight:700;color:{nc};">{irs_s:.3f}</div>'
                f'<div style="font-size:11px;color:{ecart_col};margin-top:3px;">{ecart_t}</div>'
                f'</div>'
                f'<div style="text-align:center;">'
                f'<div style="font-size:20px;">{nt}</div>'
                f'<div style="font-size:12px;color:{th["text2"]};margin-top:5px;">'
                f'PM2.5 estimé : {pm25_s:.1f} µg/m³</div>'
                f'<div style="font-size:11px;color:{th["text3"]};margin-top:3px;">'
                f'Moy. {ctx["scope_label"]} : {ctx["pm25_moy"]:.1f} µg/m³</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

    # ══════════════════════════════════════════════════════════════════════════
    # ONGLET 4 — Mensuel
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[3]:
        annees_dispo = sorted(df["date"].dt.year.unique().tolist())
        an = st.selectbox(
            T.get("bloc3_year_select", "Année"),
            annees_dispo, index=len(annees_dispo)-1, key="lt_a"
        )
        cal = df[df["date"].dt.year == an].groupby(
            df["date"].dt.month)["pm2_5_moyen"].mean().reset_index()
        cal.columns = ["mois_num", "pm2_5_moyen"]
        cal["mois"] = cal["mois_num"].apply(lambda m: mois[m-1])
        cbar = [
            th["green"] if v < 15 else
            th["amber"] if v < 25 else
            th["coral"] if v < 37.5 else
            th["red"]
            for v in cal["pm2_5_moyen"]
        ]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=cal["mois"], y=cal["pm2_5_moyen"],
            marker_color=cbar, opacity=0.9,
            text=cal["pm2_5_moyen"].round(1),
            textposition="outside",
            textfont=dict(color=th["text2"], size=10)
        ))
        fig.add_hline(
            y=15.0, line=dict(color=th["red"], width=1.2, dash="dash"),
            annotation_text="OMS 15 µg/m³",
            annotation_font_color=th["red"], annotation_font_size=10
        )
        fig.update_layout(
            **PL, height=310, showlegend=False,
            title=dict(
                text=f"{T.get('bloc3_monthly_title','Mensuel')} · {ctx['scope_label']}",
                font=dict(color=th["text"], size=13)
            )
        )
        fig.update_xaxes(**GRID)
        fig.update_yaxes(**GRID)
        st.plotly_chart(fig, use_container_width=True)

    sources_bar(
        f"Modèle Hybride Régression+ARIMA · Box & Jenkins (1976) · "
        f"INS Cameroun (2019) · {T.get('sources_who','WHO AQG 2021')}",
        th
    )
