import streamlit as st
import plotly.graph_objects as go
from utils import get_context, banner, img_card, kpi_box, sources_bar, empty_state, POLLUANTS, risk_color
from assets import IMAGES

def render(profil):
    ctx = get_context()
    df=ctx["df"]; th=ctx["th"]; T=ctx["T"]; lang=ctx["lang"]

    banner(IMAGES["kpi_banner"], 185,
           f"{T['bloc2_label']} · {ctx['scope_label']}",
           T["bloc2_chart1_title"], th, accent=th["blue"], tint_hex="#0ea5e9", tint_strength=0.30)

    if len(df) == 0: empty_state(T, th); return

    cols = st.columns(6)
    with cols[0]: kpi_box(f"{ctx['pm25_moy']:.1f} µg/m³", T["bloc2_kpi_pm25_label"],
        f"{T['bloc2_kpi_pm25_sub']} · {ctx['scope_annees']}",
        th["red"] if ctx["pm25_moy"]>15 else th["green"], th)
    with cols[1]: kpi_box(f"{ctx['irs_moy']:.3f}", T["bloc2_kpi_irs_label"],
        T["bloc2_kpi_irs_sub"].format(level=ctx["irs_label"]), ctx["irs_color"], th)
    with cols[2]: kpi_box(f"{ctx['n_dep_oms']}/{ctx['n_villes']}", T["bloc2_kpi_cities_label"],
        f"{ctx['n_dep_oms']/max(ctx['n_villes'],1)*100:.0f}% · {ctx['scope_annees']}", th["amber"], th)
    with cols[3]: kpi_box(ctx["poll_dom"], T["bloc2_kpi_pollutant_label"],
        T["bloc2_kpi_pollutant_sub"], th["blue"], th)
    with cols[4]: kpi_box(ctx["tendance"],
        T["bloc2_kpi_trend_label"].format(year=ctx["an_max"]-1),
        T["bloc2_kpi_trend_sub"].format(y1=ctx["an_max"]-1, y2=ctx["an_max"]),
        ctx["tend_color"], th)
    with cols[5]: kpi_box(f"{len(df):,}", T["bloc2_kpi_obs_label"],
        T["bloc2_kpi_obs_sub"], th["purple"], th)

    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

    PL = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
              font=dict(color=th["text2"], size=12), margin=dict(l=44,r=20,t=44,b=36))
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False)

    # ── Ligne 1 : Tendance mensuelle + Saisonnalité ──────────────────────
    c1, c2 = st.columns(2)
    with c1:
        men = df.groupby(df["date"].dt.to_period("M"))["pm2_5_moyen"].mean().reset_index()
        men["date"] = men["date"].dt.to_timestamp()
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=men["date"], y=men["pm2_5_moyen"], mode="lines",
            line=dict(color=th["blue"],width=2), fill="tozeroy",
            fillcolor=f"rgba(14,165,233,0.07)"))
        fig1.add_hline(y=15.0, line=dict(color=th["red"],width=1,dash="dash"),
            annotation_text=T["who_threshold"], annotation_font_color=th["red"], annotation_font_size=10)
        fig1.update_layout(**PL, height=260, showlegend=False,
            title=dict(text=f"{T['bloc2_chart1_title']} · {ctx['scope_label']}",
                       font=dict(color=th["text"], size=16, weight="bold")))
        fig1.update_xaxes(**GRID); fig1.update_yaxes(**GRID)
        st.plotly_chart(fig1, width="stretch")

    with c2:
        lbl_s = "Saisonnalité PM2.5 · Moyenne mensuelle" if lang == "fr" else "PM2.5 Seasonality · Monthly average"
        tend_men = df.groupby(df["date"].dt.month)["pm2_5_moyen"].mean().reset_index()
        tend_men.columns = ["mois", "pm2_5_moyen"]
        mois_n = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"] if lang == "fr" else \
                   ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        tend_men["mois_label"] = tend_men["mois"].apply(lambda m: mois_n[m-1])

        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=tend_men["mois_label"], y=tend_men["pm2_5_moyen"], mode="lines+markers",
            line=dict(color=th["blue"], width=3, shape='spline'),
            marker=dict(size=7, color=th["blue"], line=dict(color=th["bg3"], width=1.5)),
            fill="tozeroy", fillcolor="rgba(14,165,233,0.07)"))
        fig_s.add_hline(y=15, line=dict(color=th["red"], width=1, dash="dash"),
            annotation_text="OMS", annotation_font_color=th["red"], annotation_font_size=9)
        fig_s.update_layout(**PL, height=280, showlegend=False,
            title=dict(text=lbl_s, font=dict(color=th["text"], size=16, weight="bold")))
        fig_s.update_xaxes(**GRID, tickfont=dict(size=9))
        fig_s.update_yaxes(**GRID)
        st.plotly_chart(fig_s, width="stretch")

    # ── Ligne 2 : Seuils OMS ────────────────────────────
    lbl6 = "Concentrations · Seuils OMS" if lang == "fr" else "Concentrations · WHO thresholds"
    c_bdr, c_txt, c_t3, c_tert = th["border_soft"], th["text"], th["text3"], th["bg_tertiary"]
    header = (
        f'<div style="display:grid;grid-template-columns:30px 1.5fr 1fr 1fr 1fr;'
        f'gap:15px;padding:12px 0;border-bottom:2px solid {c_bdr};font-size:13px;'
        f'text-transform:uppercase;letter-spacing:.08em;color:{c_t3};font-weight:700;">'
        '<div></div><div>Polluant</div>'
        '<div style="text-align:right;">Conc.</div>'
        '<div style="text-align:right;">OMS</div>'
        '<div style="text-align:center;">État</div></div>'
    )
    rows_data = []
    for p in POLLUANTS:
        if p["col"] in df.columns:
            moy = float(df[p["col"]].mean())
            rc = risk_color(moy, p["seuil"], th)
            ratio = moy / p["seuil"]
            badge = "✅" if moy <= p["seuil"] else ("⚠️" if moy <= p["seuil"] * 1.5 else "🔴")
            nom_p = p["nom_fr"] if lang == "fr" else p["nom_en"]
            
            rows_data.append({
                "ratio": ratio,
                "html": (
                    f'<div style="display:grid;grid-template-columns:30px 1.5fr 1fr 1fr 1fr;'
                    f'gap:15px;padding:22px 0;border-bottom:1px solid {c_bdr}33;align-items:center;">'
                    f'<div style="width:14px;height:14px;border-radius:50%;background:{rc};'
                    f'box-shadow:0 0 12px {rc}66;"></div>'
                    f'<div style="font-size:16px;font-weight:700;color:{c_txt};">{nom_p}</div>'
                    f'<div style="font-size:22px;color:{rc};font-weight:800;text-align:right;font-family:monospace;'
                    f'text-shadow:0 0 8px {rc}33;">{moy:.1f}</div>'
                    f'<div style="font-size:15px;color:{c_t3};text-align:right;font-family:monospace;opacity:0.7;">{p["seuil"]}</div>'
                    f'<div style="font-size:26px;text-align:center;">{badge}</div></div>'
                )
            })

    # Tri par ratio décroissant
    rows_data.sort(key=lambda x: x["ratio"], reverse=True)
    rows_p = [r["html"] for r in rows_data]

    html_poll = (
        f'<div style="background:{c_tert};border:1px solid {c_bdr};border-radius:10px;'
        'padding:15px 20px;height:auto;box-sizing:border-box;">'
        f'<div style="font-size:18px;font-weight:800;color:{c_txt};margin-bottom:16px;'
        f'padding-bottom:10px;border-bottom:3px solid {th["blue"]};">⚗️ {lbl6}</div>'
        + header + "".join(rows_p) + '</div>'
    )
    st.markdown(html_poll, unsafe_allow_html=True)

    sources_bar(f"{T['sources_who']} · {T['sources_cecc']} · {T['sources_bauer']}", th)
