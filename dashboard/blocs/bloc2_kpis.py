import streamlit as st
import plotly.graph_objects as go
from utils import get_context, banner, img_card, kpi_box, sources_bar, empty_state, POLLUANTS, risk_color
from assets import IMAGES

def render(profil):
    ctx = get_context()
    df=ctx["df"]; th=ctx["th"]; T=ctx["T"]; lang=ctx["lang"]

    col_banner, col_filters = st.columns([1, 1], gap="large")
    with col_banner:
        banner(IMAGES["kpi_banner"], 120,
               T['bloc2_label'],
               "", th, accent=th["blue"], tint_hex="#0ea5e9", tint_strength=0.30)

    if len(df) == 0: empty_state(T, th); return

    # ── Filtres dynamiques Région / Villes ─────────────────────────────────────
    toutes_regions = "Toutes les régions" if lang == "fr" else "All regions"
    toutes_villes  = "Toutes les villes"  if lang == "fr" else "All cities"
    
    all_regions = sorted(df["region"].dropna().unique().tolist())
    
    with col_filters:
        st.markdown(f"""
        <style>
        .stMultiSelect label {{
            font-size: 14px !important;
            font-weight: 900 !important;
            color: #f0f9ff !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        /* Style des options (tags) DEJA selectionnées */
        .stMultiSelect [data-baseweb="tag"] {{
            background-color: #0ea5e9 !important;
        }}
        .stMultiSelect [data-baseweb="tag"] span {{
            color: #ffffff !important;
            font-weight: 900 !important;
            font-size: 13px !important;
        }}
        /* Assurer la visibilité du 'x' pour fermer le tag */
        .stMultiSelect [data-baseweb="tag"] svg {{
            color: #ffffff !important;
        }}
        </style>
        <div style='height:20px;'></div>
        """, unsafe_allow_html=True)

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            sel_regions = st.multiselect(
                "**CHOIX DES RÉGIONS**", 
                [toutes_regions] + all_regions, 
                default=[toutes_regions],
                key="kpi_reg_filter"
            )
            
        is_all_regions = (toutes_regions in sel_regions) or (len(sel_regions) == 0)
        
        if is_all_regions:
            cities_options = [toutes_villes]
            _sel_regions_effective = all_regions
        else:
            _df_reg = df[df["region"].isin(sel_regions)]
            cities_options = [toutes_villes] + sorted(_df_reg["ville"].dropna().unique().tolist())
            _sel_regions_effective = sel_regions

        with f_col2:
            if is_all_regions:
                sel_villes = st.multiselect(
                    "**VILLES PAR RÉGION**", 
                    cities_options, 
                    default=[toutes_villes],
                    disabled=True,
                    key="kpi_vil_filter_disabled"
                )
                _sel_villes_effective = df["ville"].dropna().unique().tolist()
            else:
                sel_villes = st.multiselect(
                    "**VILLES PAR RÉGION**", 
                    cities_options, 
                    default=[toutes_villes],
                    key="kpi_vil_filter_active"
                )
                if (toutes_villes in sel_villes) or (len(sel_villes) == 0):
                    _sel_villes_effective = sorted(df[df["region"].isin(_sel_regions_effective)]["ville"].dropna().unique().tolist())
                else:
                    _sel_villes_effective = sel_villes

    # ── Application du filtre local ────────────────────────────────────────────
    df_local = df[(df["region"].isin(_sel_regions_effective)) & (df["ville"].isin(_sel_villes_effective))]

    if len(df_local) == 0:
        empty_state(T, th)
        return

    # ── Calculs KPI locaux ─────────────────────────────────────────────────────
    pm25_moy = float(df_local["pm2_5_moyen"].mean())
    irs_moy  = float(df_local["IRS"].mean()) if "IRS" in df_local.columns else 0.0

    p50, p75, p90 = ctx["p50"], ctx["p75"], ctx["p90"]
    if   irs_moy < p50: irs_label, irs_col = T.get("level_faible", "FAIBLE"), th["green"]
    elif irs_moy < p75: irs_label, irs_col = T.get("level_modere", "MODÉRÉ"), th["amber"]
    elif irs_moy < p90: irs_label, irs_col = T.get("level_eleve",  "ÉLEVÉ"),  th["orange"]
    else:               irs_label, irs_col = T.get("level_critique","CRITIQUE"), th["red"]

    SEUIL_AQG = 15
    n_dep_oms = int((df_local.groupby("ville")["pm2_5_moyen"].mean() > SEUIL_AQG).sum())
    n_villes  = df_local["ville"].nunique()

    if "polluant_dominant" in df_local.columns and not df_local["polluant_dominant"].empty:
        counts = df_local["polluant_dominant"].value_counts()
        poll_dom = counts.index[0] if len(counts) > 0 else "PM2.5"
    else:
        poll_dom = "PM2.5"

    an_max = df_local["date"].dt.year.max()
    an_min = df_local["date"].dt.year.min()
    scope_annees = str(an_min) if an_min == an_max else f"{an_min}–{an_max}"
    
    df_max = df_local[df_local["date"].dt.year == an_max]
    df_prec = df_local[df_local["date"].dt.year == an_max - 1]
    pm25_fin = float(df_max["pm2_5_moyen"].mean()) if len(df_max)>0 else pm25_moy
    pm25_prec = float(df_prec["pm2_5_moyen"].mean()) if len(df_prec)>0 else pm25_moy
    delta = pm25_fin - pm25_prec
    tendance = f"↑ +{delta:.1f}" if delta > 0 else f"↓ {delta:.1f}"
    tend_color = th["red"] if delta > 0 else th["green"]

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    # ── KPIs Affichage ─────────────────────────────────────────────────────────
    cols = st.columns(6)
    with cols[0]: kpi_box(f"{pm25_moy:.1f} µg/m³", T["bloc2_kpi_pm25_label"],
        f"{T['bloc2_kpi_pm25_sub']} · {scope_annees}",
        th["red"] if pm25_moy>15 else th["green"], th)
    with cols[1]: kpi_box(f"{irs_moy:.3f}", T["bloc2_kpi_irs_label"],
        T["bloc2_kpi_irs_sub"].format(level=irs_label), irs_col, th)
    with cols[2]: kpi_box(f"{n_dep_oms}/{n_villes}", T["bloc2_kpi_cities_label"],
        f"{n_dep_oms/max(n_villes,1)*100:.0f}% · {scope_annees}", th["amber"], th)
    with cols[3]: kpi_box(poll_dom, T["bloc2_kpi_pollutant_label"],
        T["bloc2_kpi_pollutant_sub"], th["blue"], th)
    with cols[4]: kpi_box(tendance,
        T["bloc2_kpi_trend_label"].format(year=an_max-1),
        T["bloc2_kpi_trend_sub"].format(y1=an_max-1, y2=an_max),
        tend_color, th)
    with cols[5]: kpi_box(f"{len(df_local):,}", T["bloc2_kpi_obs_label"],
        T["bloc2_kpi_obs_sub"], th["purple"], th)

    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)

    # ── 3 Colonnes sur la même ligne ───────────────────────────────────────────
    PL = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
              font=dict(color=th["text2"], size=12), margin=dict(l=40,r=15,t=40,b=30))
    # Police des axes ultra lisible (blanche et en gras/épaisse)
    font_axes = dict(color="#ffffff", size=12, family="Arial Black, Inter, sans-serif")
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False, tickfont=font_axes)

    c1, c2, c3 = st.columns([1, 1, 1])
    
    # ── Graphique 1 : Tendance mensuelle
    with c1:
        men = df_local.groupby(df_local["date"].dt.to_period("M"))["pm2_5_moyen"].mean().reset_index()
        men["date"] = men["date"].dt.to_timestamp()
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=men["date"], y=men["pm2_5_moyen"], mode="lines",
            line=dict(color=th["blue"],width=2), fill="tozeroy",
            fillcolor=f"rgba(14,165,233,0.07)"))
        fig1.add_hline(y=15.0, line=dict(color=th["red"],width=1,dash="dash"),
            annotation_text=T["who_threshold"], annotation_font_color=th["red"], annotation_font_size=10)
        
        scope_lbl = "National" if is_all_regions and (toutes_villes in sel_villes or len(sel_villes)==0) else "Filtré"
        
        fig1.update_layout(**PL, height=280, showlegend=False,
            title=dict(text=f"{T['bloc2_chart1_title']} · {scope_lbl}",
                       font=dict(color=th["text"], size=14, weight="bold")))
        fig1.update_xaxes(**GRID); fig1.update_yaxes(**GRID)
        st.plotly_chart(fig1, use_container_width=True)

    # ── Graphique 2 : Saisonnalité (qui vient au milieu maintenant)
    with c2:
        lbl_s = "Saisonnalité PM2.5 · Moyenne" if lang == "fr" else "PM2.5 Seasonality"
        tend_men = df_local.groupby(df_local["date"].dt.month)["pm2_5_moyen"].mean().reset_index()
        tend_men.columns = ["mois", "pm2_5_moyen"]
        mois_n = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"] if lang == "fr" else \
                   ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        # S'assurer que les mois sont entiers pour l'indexation
        tend_men["mois_label"] = tend_men["mois"].apply(lambda m: mois_n[int(m)-1])

        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=tend_men["mois_label"], y=tend_men["pm2_5_moyen"], mode="lines+markers",
            line=dict(color=th["blue"], width=3, shape='spline'),
            marker=dict(size=7, color=th["blue"], line=dict(color=th["bg3"], width=1.5)),
            fill="tozeroy", fillcolor="rgba(14,165,233,0.07)"))
        fig_s.add_hline(y=15, line=dict(color=th["red"], width=1, dash="dash"),
            annotation_text="OMS", annotation_font_color=th["red"], annotation_font_size=9)
        fig_s.update_layout(**PL, height=280, showlegend=False,
            title=dict(text=lbl_s, font=dict(color=th["text"], size=14, weight="bold")))
        fig_s.update_xaxes(**GRID)
        fig_s.update_yaxes(**GRID)
        st.plotly_chart(fig_s, use_container_width=True)

    # ── Tableau : Seuils OMS (qui vient à droite et devient non scrollable)
    with c3:
        lbl6 = "Concentrations · Seuils OMS" if lang == "fr" else "Concentrations · WHO thresholds"
        c_bdr, c_txt, c_t3, c_tert = th["border_soft"], th["text"], th["text3"], th["bg_tertiary"]
        header = (
            f'<div style="display:grid;grid-template-columns:20px 1.5fr 1fr 1fr 1fr;'
            f'gap:6px;padding:4px 0;border-bottom:2px solid {c_bdr};font-size:10px;'
            f'text-transform:uppercase;letter-spacing:.05em;color:{c_t3};font-weight:700;">'
            '<div></div><div>Polluant</div>'
            '<div style="text-align:right;">Conc.</div>'
            '<div style="text-align:right;">OMS</div>'
            '<div style="text-align:center;">État</div></div>'
        )
        rows_data = []
        for p in POLLUANTS:
            if p["col"] in df_local.columns:
                moy = float(df_local[p["col"]].mean())
                rc = risk_color(moy, p["seuil"], th)
                ratio = moy / p["seuil"]
                badge = "✅" if moy <= p["seuil"] else ("⚠️" if moy <= p["seuil"] * 1.5 else "🔴")
                nom_p = p["nom_fr"] if lang == "fr" else p["nom_en"]
                
                rows_data.append({
                    "ratio": ratio,
                    "html": (
                        f'<div style="display:grid;grid-template-columns:20px 1.5fr 1fr 1fr 1fr;'
                        f'gap:6px;padding:6px 0;border-bottom:1px solid {c_bdr}33;align-items:center;">'
                        f'<div style="width:10px;height:10px;border-radius:50%;background:{rc};'
                        f'box-shadow:0 0 6px {rc}66;"></div>'
                        f'<div style="font-size:12px;font-weight:700;color:{c_txt};">{nom_p}</div>'
                        f'<div style="font-size:14px;color:{rc};font-weight:800;text-align:right;font-family:monospace;'
                        f'text-shadow:0 0 6px {rc}33;">{moy:.1f}</div>'
                        f'<div style="font-size:11px;color:{c_t3};text-align:right;font-family:monospace;opacity:0.7;">{p["seuil"]}</div>'
                        f'<div style="font-size:15px;text-align:center;">{badge}</div></div>'
                    )
                })

        rows_data.sort(key=lambda x: x["ratio"], reverse=True)
        rows_p = [r["html"] for r in rows_data]

        # Table extra compactisée pour tenir dans 280px max sans scroll
        html_poll = (
            f'<div style="background:{c_tert};border:1px solid {c_bdr};border-radius:10px;'
            'padding:8px 12px;height:auto;box-sizing:border-box;">'
            f'<div style="font-size:13px;font-weight:800;color:{c_txt};margin-bottom:6px;'
            f'padding-bottom:4px;border-bottom:3px solid {th["blue"]};">⚗️ {lbl6}</div>'
            + header + "".join(rows_p) + '</div>'
        )
        st.markdown(html_poll, unsafe_allow_html=True)

    sources_bar(f"{T['sources_who']} · {T['sources_cecc']} · {T['sources_bauer']}", th)
