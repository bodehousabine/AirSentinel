"""blocs/bloc1_carte.py — Carte interactive · données du jour · MarkerCluster"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils import get_context, banner, img_card, sources_bar, empty_state
from assets import IMAGES

# Polluants avec seuils OMS AQG 2021
POLLUANTS = [
    {"col":"pm2_5_moyen", "nom_fr":"PM2.5",  "nom_en":"PM2.5",  "seuil":15,  "unite":"µg/m³", "color":"#f87171"},
    {"col":"pm10_moyen",  "nom_fr":"PM10",   "nom_en":"PM10",   "seuil":45,  "unite":"µg/m³", "color":"#fb923c"},
    {"col":"no2_moyen",   "nom_fr":"NO₂",    "nom_en":"NO₂",    "seuil":25,  "unite":"µg/m³", "color":"#fbbf24"},
    {"col":"so2_moyen",   "nom_fr":"SO₂",    "nom_en":"SO₂",    "seuil":40,  "unite":"µg/m³", "color":"#a78bfa"},
    {"col":"ozone_moyen", "nom_fr":"Ozone",  "nom_en":"Ozone",  "seuil":100, "unite":"µg/m³", "color":"#38bdf8"},
    {"col":"co_moyen",    "nom_fr":"CO",     "nom_en":"CO",     "seuil":4000,"unite":"µg/m³", "color":"#34d399"},
]

def _risk_color(val, seuil, th):
    if val <= seuil:        return th["green"]
    if val <= seuil * 1.5:  return th["amber"]
    if val <= seuil * 2.5:  return th["coral"]
    return                         th["red"]

def _niveau_label(pm25, lang):
    if   pm25 <= 15:   return ("🟢 FAIBLE",    "🟢 LOW")       [lang=="en"]
    elif pm25 <= 25:   return ("🟡 MODÉRÉ",    "🟡 MODERATE")  [lang=="en"]
    elif pm25 <= 37.5: return ("🟠 ÉLEVÉ",     "🟠 HIGH")      [lang=="en"]
    elif pm25 <= 50:   return ("🔴 TRÈS ÉLEVÉ","🔴 VERY HIGH") [lang=="en"]
    elif pm25 <= 75:   return ("🟣 CRITIQUE",  "🟣 CRITICAL")  [lang=="en"]
    else:              return ("⚫ DANGEREUX",  "⚫ DANGEROUS") [lang=="en"]

def render(profil):
    ctx  = get_context()
    df   = ctx["df_brut"]   # ← données brutes complètes
    th   = ctx["th"]
    T    = ctx["T"]
    lang = ctx["lang"]

    banner(
        IMAGES["carte_banner"], 190,
        f"{T['bloc1_label']}",
        T["bloc1_subtitle"], th,
        accent=th["teal"], tint_hex="#00d4b1", tint_strength=0.32
    )

    if len(df) == 0:
        empty_state(T, th)
        return

    # ── Sélecteur mode ────────────────────────────────────────────────────────
    col_mode, col_ville = st.columns([1, 2])
    with col_mode:
        mode = st.radio(
            "Mode" if lang == "fr" else "Mode",
            ["📅 Aujourd'hui", "📊 Historique"] if lang == "fr"
            else ["📅 Today", "📊 Historical"],
            horizontal=True,
            key="carte_mode"
        )
    mode_today = "Aujourd'hui" in mode or "Today" in mode

    # ── Filtrer selon le mode ─────────────────────────────────────────────────
    if mode_today:
        date_max = df["date"].max()
        df_carte = df[df["date"] == date_max].copy()
        periode_label = str(date_max.date())
    else:
        an_min, an_max_sel = st.session_state.get("annee_sel", (int(df["date"].dt.year.min()), int(df["date"].dt.year.max())))
        df_carte = df[
            (df["date"].dt.year >= an_min) &
            (df["date"].dt.year <= an_max_sel)
        ].copy()
        periode_label = f"{an_min}–{an_max_sel}"

    # ── Filtre ville (dans la page) ───────────────────────────────────────────
    with col_ville:
        villes_dispo = sorted(df_carte["ville"].unique().tolist())
        all_label    = "Toutes les villes" if lang == "fr" else "All cities"
        ville_sel    = st.selectbox(
            "🏙️ Ville" if lang == "fr" else "🏙️ City",
            [all_label] + villes_dispo,
            key="carte_ville_sel"
        )

    # ── Agréger ───────────────────────────────────────────────────────────────
    agg = df_carte.groupby("ville").agg(
        pm2_5_moyen=("pm2_5_moyen", "mean"),
        IRS=("IRS", "mean"),
        latitude=("latitude", "first"),
        longitude=("longitude", "first"),
        region=("region", "first"),
    ).reset_index()

    PL   = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
                font=dict(color=th["text2"], size=12), margin=dict(l=44,r=20,t=44,b=36))
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False)

    # ══ CARTE ════════════════════════════════════════════════════════════════
    col_map, col_side = st.columns([3, 1])
    with col_map:
        fig = go.Figure()

        if ville_sel != all_label:
            # Mode ville sélectionnée
            autres = agg[agg["ville"] != ville_sel]
            sel    = agg[agg["ville"] == ville_sel]

            if len(autres) > 0:
                fig.add_trace(go.Scattermapbox(
                    lat=autres["latitude"], lon=autres["longitude"],
                    mode="markers",
                    marker=dict(size=8, color="rgba(107,122,150,0.45)"),
                    hoverinfo="skip", showlegend=False
                ))
            if len(sel) > 0:
                pm_val = float(sel["pm2_5_moyen"].values[0])
                fig.add_trace(go.Scattermapbox(
                    lat=sel["latitude"], lon=sel["longitude"],
                    mode="markers+text",
                    marker=dict(
                        size=28,
                        color=[pm_val],
                        colorscale=[[0,th["green"]],[0.4,th["amber"]],[0.7,th["coral"]],[1,th["red"]]],
                        cmin=5, cmax=80,
                        colorbar=dict(title="PM2.5", thickness=18, len=0.8, y=0.5)
                    ),
                    text=sel["ville"],
                    textposition="top center",
                    textfont=dict(size=14, color=th["teal"]),
                    hovertemplate=(
                        "<b>%{text}</b><br>"
                        f"PM2.5 : {pm_val:.1f} µg/m³<br>"
                        f"Niveau : {_niveau_label(pm_val, lang)}<br>"
                        f"Période : {periode_label}"
                        "<extra></extra>"
                    )
                ))
                geo_center = dict(lat=float(sel["latitude"].values[0]), lon=float(sel["longitude"].values[0]))
                geo_zoom   = 8.5
        else:
            # Mode toutes les villes
            # Couleurs selon PM2.5
            colors = [
                th["green"]  if v <= 15   else
                th["amber"]  if v <= 25   else
                th["coral"]  if v <= 37.5 else
                th["red"]
                for v in agg["pm2_5_moyen"]
            ]
            # Taille des marqueurs proportionnelle mais avec un minimum
            sizes = agg["pm2_5_moyen"].clip(12, 30).tolist()

            fig.add_trace(go.Scattermapbox(
                lat=agg["latitude"],
                lon=agg["longitude"],
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=agg["pm2_5_moyen"],
                    colorscale=[[0,th["green"]],[0.4,th["amber"]],[0.7,th["coral"]],[1,th["red"]]],
                    cmin=5, cmax=80,
                    colorbar=dict(title="PM2.5 µg/m³", thickness=18, len=0.8, y=0.5),
                    opacity=0.85,
                ),
                text=agg["ville"],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "PM2.5 : %{marker.color:.1f} µg/m³<br>"
                    "IRS : %{customdata[0]:.3f}<br>"
                    "Région : %{customdata[1]}<br>"
                    f"Période : {periode_label}"
                    "<extra></extra>"
                ),
                customdata=np.stack([agg["IRS"], agg["region"]], axis=1),
                showlegend=False
            ))
            geo_center = dict(lat=7.5, lon=12.8)
            geo_zoom   = 4.85

            qualite_lbl = "Qualité de l'air" if lang == "fr" else "Air quality"
            ville_lbl   = f" · {ville_sel}" if ville_sel != all_label else " · 40 villes"
            titre_carte = f"{qualite_lbl} · {periode_label}{ville_lbl}"
            fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=th["plot_bg"],
            font=dict(color=th["text2"], size=12),
            margin=dict(l=0, r=0, t=44, b=0),
            height=600,
            title=dict(text=titre_carte, font=dict(color=th["text"], size=14), y=0.98),
            mapbox=dict(style="open-street-map", center=geo_center, zoom=geo_zoom)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Légende couleurs PM2.5
        st.markdown(
            f"<div style='display:flex;gap:16px;flex-wrap:wrap;margin-top:6px;"
            f"font-size:10px;color:{th['text3']};'>"
            f"<span>🟢 &lt; 15 µg/m³ — {'Conforme OMS' if lang=='fr' else 'WHO compliant'}</span>"
            f"<span>🟡 15–25 — {'Modéré' if lang=='fr' else 'Moderate'}</span>"
            f"<span>🟠 25–37.5 — {'Élevé' if lang=='fr' else 'High'}</span>"
            f"<span>🔴 &gt; 37.5 — {'Critique' if lang=='fr' else 'Critical'}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_side:
        img_card(IMAGES["carte_banner"], 90, T["bloc1_satellite_label"],
                 T["bloc1_satellite_desc"], th, tint_hex="#00d4b1")

        n_dep = int((agg["pm2_5_moyen"] > 15).sum())
        pct   = f"{n_dep/max(len(agg),1)*100:.0f}%"

        st.markdown(f"""
        <div style="background:{th['bg_tertiary']};border:1px solid {th['border_soft']};
                    border-radius:10px;padding:12px;margin-top:8px;">
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:.08em;
                        color:{th['text3']};margin-bottom:8px;">{T['bloc1_oms_title']}</div>
            {"".join([
                f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:6px;">'
                f'<div style="width:9px;height:9px;border-radius:50%;background:{co};flex-shrink:0;"></div>'
                f'<div><div style="font-size:10px;color:{th["text"]};">{va}</div>'
                f'<div style="font-size:9px;color:{th["text3"]};">{la}</div></div></div>'
                for co, va, la in [
                    (th["green"],  "< 15 µg/m³",  T["bloc1_oms_conform"]),
                    (th["amber"],  "15–25",        "IT-4"),
                    (th["coral"],  "25–37.5",      "IT-3"),
                    (th["red"],    "> 37.5",        "IT-1/2"),
                ]
            ])}
        </div>
        <div style="background:rgba(239,68,68,0.10);border:1px solid rgba(239,68,68,0.22);
                    border-radius:10px;padding:12px;margin-top:8px;text-align:center;">
            <div style="font-size:26px;font-weight:600;color:{th['red']};">{n_dep}</div>
            <div style="font-size:10px;color:{th['text2']};">{T['bloc1_cities_above']}</div>
            <div style="font-size:9px;color:{th['text3']};margin-top:2px;">
                {pct} · {periode_label}
            </div>
        </div>""", unsafe_allow_html=True)

        # Top 3 villes les plus polluées aujourd'hui
        top3 = agg.nlargest(3, "pm2_5_moyen")
        lbl_top = "🏆 Top 3 villes" if lang == "fr" else "🏆 Top 3 cities"
        rows_top = ""
        for rank, (_, row) in enumerate(top3.iterrows(), 1):
            color = th["red"] if row["pm2_5_moyen"] > 37.5 else th["coral"] if row["pm2_5_moyen"] > 25 else th["amber"]
            rows_top += (
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:center;padding:5px 0;border-bottom:1px solid {th["border_soft"]}22;">'
                f'<span style="font-size:11px;color:{th["text"]};">{rank}. {row["ville"]}</span>'
                f'<span style="font-size:11px;font-weight:600;color:{color};">{row["pm2_5_moyen"]:.1f}</span>'
                f'</div>'
            )
        st.markdown(
            f'<div style="background:{th["bg_tertiary"]};border:1px solid {th["border_soft"]};'
            f'border-radius:10px;padding:12px;margin-top:8px;">'
            f'<div style="font-size:10px;text-transform:uppercase;letter-spacing:.08em;'
            f'color:{th["text3"]};margin-bottom:8px;">{lbl_top} · {periode_label}</div>'
            f'{rows_top}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<hr style='border-color:rgba(99,160,255,0.10);margin:24px 0 20px;'>", unsafe_allow_html=True)

    # ══ ANALYSES ENRICHIES ════════════════════════════════════════════════════
    st.markdown(
        f"<div style='font-size:16px;font-weight:600;color:{th['text']};margin-bottom:18px;'>"
        f"📊 {'Analyses détaillées' if lang=='fr' else 'Detailed analyses'} · {periode_label}</div>",
        unsafe_allow_html=True
    )

    ca, cb, cc = st.columns(3)

    with ca:
        # PM2.5 par région
        lbl  = "PM2.5 moyen par région" if lang == "fr" else "Avg PM2.5 by region"
        pm_reg = df_carte.groupby("region")["pm2_5_moyen"].mean().sort_values(ascending=False)
        colors = [_risk_color(v, 15, th) for v in pm_reg.values]
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            x=pm_reg.index, y=pm_reg.values, orientation="v",
            marker_color=colors, opacity=0.88,
            text=[f"{v:.1f}" for v in pm_reg.values],
            textposition="outside", textfont=dict(color=th["text2"], size=9)
        ))
        fig_reg.add_hline(y=15, line=dict(color=th["red"], width=1.2, dash="dash"),
            annotation_text="OMS 15", annotation_font_color=th["red"], annotation_font_size=9)
        fig_reg.update_layout(**PL, height=280, showlegend=False,
            title=dict(text=lbl, font=dict(color=th["text"], size=12)))
        fig_reg.update_xaxes(**GRID, tickfont=dict(size=8), tickangle=-35)
        fig_reg.update_yaxes(**GRID)
        st.plotly_chart(fig_reg, use_container_width=True)

    with cb:
        # Top 3 polluants dépassant OMS
        lbl3 = "Dépassements OMS · Top polluants" if lang == "fr" else "WHO exceedances · Top pollutants"
        rows_t3 = []
        for p in POLLUANTS:
            if p["col"] not in df_carte.columns:
                continue
            moy = float(df_carte[p["col"]].mean())
            pct_v = min(moy / p["seuil"] * 100, 200)
            mc  = _risk_color(moy, p["seuil"], th)
            nom = p["nom_fr"] if lang == "fr" else p["nom_en"]
            rows_t3.append(
                f'<div style="margin-bottom:9px;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:2px;">'
                f'<span style="font-size:11px;color:{th["text"]};font-weight:500;">{nom}</span>'
                f'<span style="font-size:11px;color:{mc};font-weight:600;">{moy:.1f} {p["unite"]}</span>'
                f'</div>'
                f'<div style="background:{th["bg_elevated"]};border-radius:3px;height:5px;overflow:hidden;">'
                f'<div style="background:{mc};height:100%;width:{min(pct_v,100):.0f}%;border-radius:3px;"></div>'
                f'</div>'
                f'<div style="font-size:9px;color:{th["text3"]};margin-top:1px;">'
                f'OMS : {p["seuil"]} {p["unite"]}</div>'
                f'</div>'
            )
        st.markdown(
            f'<div style="background:{th["bg_tertiary"]};border:1px solid {th["border_soft"]};'
            f'border-radius:10px;padding:12px 14px;height:280px;box-sizing:border-box;overflow-y:auto;">'
            f'<div style="font-size:11px;font-weight:600;color:{th["text"]};margin-bottom:12px;">'
            f'🏆 {lbl3}</div>'
            f'{"".join(rows_t3)}</div>',
            unsafe_allow_html=True
        )

    with cc:
        # Tableau concentrations vs seuils OMS
        lbl6  = "Concentrations · Seuils OMS" if lang == "fr" else "Concentrations · WHO thresholds"
        rows_p = []
        for p in POLLUANTS:
            if p["col"] not in df_carte.columns:
                continue
            moy   = float(df_carte[p["col"]].mean())
            rc    = _risk_color(moy, p["seuil"], th)
            badge = "✅" if moy <= p["seuil"] else ("⚠️" if moy <= p["seuil"] * 1.5 else "🔴")
            nom_p = p["nom_fr"] if lang == "fr" else p["nom_en"]
            rows_p.append(
                f'<div style="display:grid;grid-template-columns:10px 1fr 70px 46px 26px;'
                f'gap:4px;padding:5px 0;border-bottom:1px solid {th["border_soft"]}22;align-items:center;">'
                f'<div style="width:8px;height:8px;border-radius:50%;background:{p["color"]};"></div>'
                f'<div style="font-size:11px;font-weight:500;color:{th["text"]};">{nom_p}</div>'
                f'<div style="font-size:10px;color:{rc};font-weight:600;text-align:right;'
                f'font-family:monospace;">{moy:.1f} {p["unite"]}</div>'
                f'<div style="font-size:10px;color:{th["text3"]};text-align:right;'
                f'font-family:monospace;">{p["seuil"]}</div>'
                f'<div style="font-size:12px;text-align:center;">{badge}</div>'
                f'</div>'
            )
        st.markdown(
            f'<div style="background:{th["bg_tertiary"]};border:1px solid {th["border_soft"]};'
            f'border-radius:10px;padding:12px 14px;height:280px;box-sizing:border-box;overflow-y:auto;">'
            f'<div style="font-size:11px;font-weight:600;color:{th["text"]};margin-bottom:8px;">'
            f'⚗️ {lbl6}</div>'
            f'<div style="display:grid;grid-template-columns:10px 1fr 70px 46px 26px;gap:4px;'
            f'padding:4px 0;border-bottom:1px solid {th["border_soft"]};font-size:9px;'
            f'text-transform:uppercase;letter-spacing:.04em;color:{th["text3"]};">'
            f'<div></div><div>Polluant</div>'
            f'<div style="text-align:right;">Conc.</div>'
            f'<div style="text-align:right;">OMS</div>'
            f'<div style="text-align:center;">⚡</div></div>'
            f'{"".join(rows_p)}</div>',
            unsafe_allow_html=True
        )

    sources_bar(f"{T['sources_who']} · {T['sources_cecc']} · {T['sources_bauer']}", th)
