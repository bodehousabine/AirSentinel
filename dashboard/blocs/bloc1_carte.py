"""blocs/bloc1_carte.py — Carte + analyses PM2.5 enrichies · toggle Aujourd'hui/Historique"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import joblib
import os
from datetime import date
from utils import get_context, banner, img_card, sources_bar, empty_state, POLLUANTS, risk_color
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    chemins = [
        os.path.join(base_dir, '..', 'models'),
        os.path.join(base_dir, '..', '..', 'models'),
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


@st.cache_data(ttl=3600)
def _predire_toutes_villes(_hash, df):
    """Prédit PM2.5 pour aujourd'hui pour toutes les villes."""
    modele, scaler, features, arima = _load_models()
    if not all(x is not None for x in [modele, scaler, features, arima]):
        return None

    resultats = []
    for ville in df['ville'].unique():
        df_v   = df[df['ville'] == ville].sort_values('date')
        region = df_v['region'].iloc[-1] if len(df_v) > 0 else 'Centre'
        zone   = _get_zone(region)
        lat    = df_v['latitude'].iloc[-1] if 'latitude' in df_v.columns else 4.0
        lon    = df_v['longitude'].iloc[-1] if 'longitude' in df_v.columns else 12.0
        try:
            last   = df_v[features].fillna(df_v[features].median()).tail(1)
            last_s = scaler.transform(last)
            p_rl   = modele.predict(last_s)[0]
            p_arima = arima[zone].forecast(steps=1).iloc[-1]
            pm25   = max(0, p_rl + p_arima)
        except:
            pm25 = float(df_v['pm2_5_moyen'].mean()) if len(df_v) > 0 else 15.0

        # IRS basé sur PM2.5 prédit
        if   pm25 <= 15:   irs = 0
        elif pm25 <= 25:   irs = 1
        elif pm25 <= 37.5: irs = 2
        elif pm25 <= 50:   irs = 3
        elif pm25 <= 75:   irs = 4
        else:              irs = 5

        resultats.append({
            'ville':       ville,
            'region':      region,
            'latitude':    lat,
            'longitude':   lon,
            'pm2_5_moyen': pm25,
            'IRS':         irs,
            'date':        pd.Timestamp(date.today()),
        })

    return pd.DataFrame(resultats)


def render(profil):
    ctx  = get_context()
    df   = ctx["df_brut"]
    th   = ctx["th"]
    T    = ctx["T"]
    lang = ctx["lang"]
    COORDS = ctx["coords"] if "coords" in ctx else {}

    banner(IMAGES["carte_banner"], 190,
           f"{T['bloc1_label']}",
           T["bloc1_subtitle"], th,
           accent=th["teal"], tint_hex="#00d4b1", tint_strength=0.32)

    if len(df) == 0:
        empty_state(T, th)
        return

    # ── Toggle Aujourd'hui / Historique + sélecteur ville ─────────────────
    col_mode, col_ville = st.columns([1, 2])
    with col_mode:
        auj_lbl  = "📅 Aujourd'hui" if lang == "fr" else "📅 Today"
        hist_lbl = "📊 Historique"  if lang == "fr" else "📊 Historical"
        mode = st.radio("Mode", [auj_lbl, hist_lbl], horizontal=True, key="carte_mode")
    mode_today = "Aujourd'hui" in mode or "Today" in mode

    if mode_today:
        # ── Données prédites pour aujourd'hui ─────────────────────────────
        df_pred = _predire_toutes_villes(len(df), df)
        if df_pred is not None and len(df_pred) > 0:
            df_carte      = df_pred.copy()
            periode_label = f"📅 {date.today().strftime('%d %b %Y')} · Prédictions"
            source_label  = "Modèle Hybride RL+ARIMA"
        else:
            # Fallback sur données réelles si modèle indisponible
            date_max      = df["date"].max()
            df_carte      = df[df["date"] == date_max].copy()
            periode_label = str(date_max.date())
            source_label  = "Données réelles"
    else:
        an_min, an_max_sel = st.session_state.get(
            "annee_sel",
            (int(df["date"].dt.year.min()), int(df["date"].dt.year.max()))
        )
        df_carte = df[
            (df["date"].dt.year >= an_min) &
            (df["date"].dt.year <= an_max_sel)
        ].copy()
        periode_label = f"{an_min}–{an_max_sel}"
        source_label  = "Données réelles"

    with col_ville:
        villes_dispo = sorted(df_carte["ville"].unique().tolist())
        all_label    = "Toutes les villes" if lang == "fr" else "All cities"
        ville_sel_carte = st.selectbox(
            "🏙️ Ville" if lang == "fr" else "🏙️ City",
            [all_label] + villes_dispo,
            key="carte_ville_sel"
        )

    # ── Agrégation ────────────────────────────────────────────────────────
    agg = df_carte.groupby("ville")[["pm2_5_moyen", "IRS"]].mean().reset_index()

    # Coordonnées depuis le dataset ou COORDS
    def get_coords(ville):
        if ville in COORDS:
            return COORDS[ville]
        row = df[df['ville'] == ville]
        if len(row) > 0 and 'latitude' in row.columns:
            return (float(row['latitude'].iloc[0]), float(row['longitude'].iloc[0]))
        return (4.0, 12.0)

    agg["lat"] = agg["ville"].apply(lambda v: get_coords(v)[0])
    agg["lon"] = agg["ville"].apply(lambda v: get_coords(v)[1])

    PL   = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
                font=dict(color=th["text2"], size=12), margin=dict(l=44,r=20,t=44,b=36))
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False)

    # ══ CARTE ════════════════════════════════════════════════════════════════
    col_map, col_side = st.columns([2, 1])
    with col_map:
        fig = go.Figure()

        if ville_sel_carte != all_label:
            autres = agg[agg["ville"] != ville_sel_carte]
            sel    = agg[agg["ville"] == ville_sel_carte]
            if len(autres) > 0:
                fig.add_trace(go.Scattermapbox(
                    lat=autres["lat"], lon=autres["lon"], mode="markers",
                    marker=dict(size=8, color="rgba(107,122,150,0.55)", allowrecolor=False),
                    hoverinfo="skip", showlegend=False))
            if len(sel) > 0:
                fig.add_trace(go.Scattermapbox(
                    lat=sel["lat"], lon=sel["lon"], mode="markers+text",
                    marker=dict(size=24, color=sel["pm2_5_moyen"],
                        colorscale=[[0,th["green"]],[0.4,th["amber"]],[0.7,th["coral"]],[1,th["red"]]],
                        cmin=5, cmax=80,
                        colorbar=dict(title="PM2.5", thickness=20, len=1.0, y=1, yanchor='top')),
                    text=sel["ville"], textposition="top center",
                    textfont=dict(size=14, color=th["teal"]),
                    hovertemplate="<b>%{text}</b><br>PM2.5 : %{marker.color:.1f} µg/m³<extra></extra>"))
                geo_center = dict(lat=float(sel["lat"].values[0]), lon=float(sel["lon"].values[0]))
                geo_zoom   = 8.5
        else:
            fig.add_trace(go.Scattermapbox(
                lat=agg["lat"], lon=agg["lon"], mode="markers",
                marker=dict(
                    size=agg["pm2_5_moyen"].clip(10, 25),
                    color=agg["pm2_5_moyen"],
                    colorscale=[[0,th["green"]],[0.4,th["amber"]],[0.7,th["coral"]],[1,th["red"]]],
                    cmin=5, cmax=80,
                    colorbar=dict(title="PM2.5 µg/m³", thickness=20, len=1.0, y=1, yanchor='top')),
                text=agg["ville"],
                hovertemplate="<b>%{text}</b><br>PM2.5 : %{marker.color:.1f} µg/m³<br>IRS : %{customdata:.3f}<extra></extra>",
                customdata=agg["IRS"]))
            geo_center = dict(lat=7.35, lon=12.35)
            geo_zoom   = 5.4

        titre_carte = f"{T['bloc1_map_title']} · {periode_label}"
        if ville_sel_carte != all_label:
            titre_carte += f" · {ville_sel_carte}"

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
            font=dict(color=th["text2"], size=12),
            margin=dict(l=0, r=0, t=35, b=0),
            height=710,
            title=dict(text=titre_carte, font=dict(color=th["text"], size=14), y=1, yanchor='top'),
            mapbox=dict(style="open-street-map", center=geo_center, zoom=geo_zoom))
        st.plotly_chart(fig, width="stretch", config={
            'scrollZoom': True,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['zoomInMapbox', 'zoomOutMapbox', 'toggleHover']
        })

        # Source des données
        st.markdown(
            f'<div style="font-size:10px;color:{th["text3"]};margin-top:4px;'
            f'font-family:DM Mono,monospace;">🔬 {source_label} · WHO AQG 2021</div>',
            unsafe_allow_html=True
        )

    with col_side:
        n_dep = int((agg["pm2_5_moyen"] > 15).sum())
        pct   = f"{n_dep/max(len(agg),1)*100:.0f}%"

        lbl_legend = "Légende · Qualité de l'Air" if lang == "fr" else "Legend · Air Quality"
        st.markdown(f"""
        <div style="background:{th['bg_tertiary']};border:1px solid {th['border_soft']};
                    border-radius:10px;padding:16px 18px;margin-top:8px;
                    box-shadow:0 4px 15px rgba(0,0,0,0.2);">
            <div style="font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;
                        color:{th['text']};margin-bottom:12px;display:flex;align-items:center;gap:8px;">
                <span style="font-size:16px;">📍</span> {lbl_legend}
            </div>
            {"".join([
                f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">'
                f'<div style="width:14px;height:14px;border-radius:50%;background:{co};flex-shrink:0;'
                f'box-shadow:0 0 8px {co}88;"></div>'
                f'<div><div style="font-size:13px;color:{th["text"]};font-weight:600;">{va}</div>'
                f'<div style="font-size:10px;color:{th["text3"]};font-weight:500;margin-top:1px;">{la}</div>'
                f'</div></div>'
                for co, va, la in [
                    (th["green"],  "< 15 µg/m³",     T["bloc1_oms_conform"]),
                    (th["amber"],  "15 – 25 µg/m³",  "Niveau modéré"),
                    (th["coral"],  "25 – 37.5 µg/m³","Alerte IT3"),
                    (th["red"],    "> 37.5 µg/m³",   "Danger critique"),
                ]
            ])}
        </div>

        <div style="background:{f'linear-gradient(135deg, {th["red"]} 0%, #7f1d1d 100%)' if n_dep > 0 else th['bg_tertiary']};
                    border:1px solid rgba(239,68,68,0.4);border-radius:12px;padding:18px 12px;
                    margin-top:12px;text-align:center;">
            <div style="font-size:42px;font-weight:800;
                        color:{'#ffffff' if n_dep > 0 else th['text']};line-height:1;">{n_dep}</div>
            <div style="font-size:12px;font-weight:700;
                        color:{'#ffffff' if n_dep > 0 else th['text']};
                        margin-top:5px;text-transform:uppercase;">{T['bloc1_cities_above']}</div>
            <div style="font-size:10px;color:{'#ffffff' if n_dep > 0 else th['text']};opacity:0.85;
                        margin-top:4px;font-family:'DM Mono',monospace;">
                {pct} · {periode_label}
            </div>
        </div>""", unsafe_allow_html=True)

        # PM2.5 par région — basé sur prédictions si mode aujourd'hui
        lbl = "PM2.5 prédit par région" if (mode_today and lang == "fr") else \
              "Avg predicted PM2.5 by region" if mode_today else \
              "PM2.5 moyen par région" if lang == "fr" else "Avg PM2.5 by region"
        pm_reg = df_carte.groupby("region")["pm2_5_moyen"].mean().sort_values(ascending=False)
        colors = [risk_color(v, 15, th) for v in pm_reg.values]
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            x=pm_reg.index, y=pm_reg.values, orientation="v",
            marker_color=colors, opacity=0.88,
            text=[f"{v:.1f}" for v in pm_reg.values],
            textposition="outside", textfont=dict(color=th["text2"], size=9)))
        fig_reg.add_hline(y=15, line=dict(color=th["red"], width=1.2, dash="dash"),
            annotation_text="OMS 15", annotation_font_color=th["red"], annotation_font_size=9)
        fig_reg.update_layout(**PL, height=350, showlegend=False,
            title=dict(text=lbl, font=dict(color=th["text"], size=12)))
        fig_reg.update_xaxes(**GRID, tickfont=dict(size=8), tickangle=-35)
        fig_reg.update_yaxes(**GRID)
        st.plotly_chart(fig_reg, width="stretch")

    st.markdown("<hr style='border-color:rgba(99,160,255,0.06);margin:8px 0 2px;'>", unsafe_allow_html=True)

    # ══ ANALYSES ENRICHIES — toujours basées sur données historiques réelles ══
    titre_analyses = "Analyses détaillées · " + periode_label
    st.markdown(f"""
    <div style="font-size:16px;font-weight:600;color:{th['text']};margin-top:-10px;margin-bottom:16px;">
        📊 {titre_analyses}
    </div>""", unsafe_allow_html=True)

    # Pour les analyses enrichies, utiliser les données historiques réelles
    df_analyse = df_carte if not mode_today else df[df["date"] == df["date"].max()].copy()

    c1, c2 = st.columns(2)

    with c1:
        lbl3 = "Top 3 polluants · National" if lang == "fr" else "Top 3 pollutants · National"
        if "polluant_dominant" in df_analyse.columns:
            top3  = df_analyse["polluant_dominant"].value_counts().head(3)
            total = top3.sum()
            medal_colors = [th["amber"], th.get("gray", "#6b7280"), th["coral"]]
            medals = ["🥇", "🥈", "🥉"]
            bg_el  = th["bg_elevated"]
            c_text = th["text"]
            c_t3   = th["text3"]
            c_bg   = th["bg_tertiary"]
            c_bdr  = th["border_soft"]
            unit   = "j" if lang == "fr" else "d"
            rows_t3 = []
            for i, (poll, cnt) in enumerate(top3.items()):
                pct_v = cnt / total * 100 if total > 0 else 0
                mc    = medal_colors[i] if i < len(medal_colors) else th["blue"]
                w     = f"{pct_v:.0f}%"
                rows_t3.append(
                    '<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">'
                    + f'<div style="font-size:20px;line-height:1;">{medals[i]}</div>'
                    + '<div style="flex:1;min-width:0;">'
                    + '<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                    + f'<span style="font-size:13px;color:{c_text};font-weight:600;">{poll}</span>'
                    + f'<span style="font-size:13px;color:{mc};font-weight:700;">{pct_v:.0f}%</span>'
                    + '</div>'
                    + f'<div style="background:{bg_el};border-radius:4px;height:8px;overflow:hidden;">'
                    + f'<div style="background:{mc};height:100%;width:{w};border-radius:4px;"></div></div>'
                    + f'<div style="font-size:10px;color:{c_t3};margin-top:2px;">{cnt:,} {unit}</div>'
                    + '</div></div>'
                )
            html_top3 = (
                f'<div style="background:{c_bg};border:1px solid {c_bdr};'
                'border-radius:12px;padding:20px 22px;height:320px;box-sizing:border-box;">'
                + f'<div style="font-size:14px;font-weight:700;color:{c_text};margin-bottom:18px;">🏆 {lbl3}</div>'
                + "".join(rows_t3)
                + '</div>'
            )
            st.markdown(html_top3, unsafe_allow_html=True)

    with c2:
        lbl4 = "Top 5 villes · Alerte critique IRS" if lang == "fr" else "Top 5 cities · Critical HRI"
        df_analyse["niv_num"] = np.searchsorted(
            [ctx["p50"], ctx["p75"], ctx["p90"]], df_analyse["IRS"].values, side="right"
        ).clip(0, 3)
        crit_v = (
            df_analyse[df_analyse["niv_num"] == 3].groupby("ville").size()
            .sort_values(ascending=False).head(5).reset_index()
        )
        crit_v.columns = ["ville", "n_jours"]
        max_j  = crit_v["n_jours"].max() if len(crit_v) > 0 else 1
        unit   = "j" if lang == "fr" else "d"
        c_red  = th["red"]
        c_cor  = th["coral"]
        c_txt  = th["text"]
        c_elev = th["bg_elevated"]
        c_tert = th["bg_tertiary"]
        c_t3   = th["text3"]
        rows_t5 = []
        if len(crit_v) == 0:
            rows_t5.append(f'<div style="font-size:11px;color:{c_t3};">Aucune ville en alerte critique.</div>')
        for _, row in crit_v.iterrows():
            pct_v = row["n_jours"] / max_j * 100
            w     = f"{pct_v:.0f}%"
            rows_t5.append(
                '<div style="margin-bottom:14px;">'
                + '<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
                + f'<span style="font-size:13px;color:{c_txt};font-weight:600;">📍 {row["ville"]}</span>'
                + f'<span style="font-size:12px;color:{c_red};font-weight:700;">{row["n_jours"]} {unit}</span>'
                + '</div>'
                + f'<div style="background:{c_elev};border-radius:4px;height:8px;overflow:hidden;">'
                + f'<div style="background:linear-gradient(to right,{c_cor},{c_red});height:100%;width:{w};border-radius:4px;"></div></div>'
                + '</div>'
            )
        html_top5 = (
            f'<div style="background:{c_tert};border:1px solid rgba(239,68,68,0.35);'
            'border-radius:12px;padding:20px 22px;height:320px;box-sizing:border-box;">'
            + f'<div style="font-size:14px;font-weight:700;color:{c_red};margin-bottom:18px;">🚨 {lbl4}</div>'
            + "".join(rows_t5)
            + '</div>'
        )
        st.markdown(html_top5, unsafe_allow_html=True)

    sources_bar(f"{T['sources_who']} · {T['sources_cecc']} · {T['sources_bauer']}", th)