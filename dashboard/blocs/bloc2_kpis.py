"""blocs/bloc2_kpis.py — KPIs · bilingue + thème"""
import streamlit as st
import plotly.graph_objects as go
from utils import get_context, banner, img_card, kpi_box, sources_bar, empty_state
from assets import IMAGES

def render(profil):
    ctx = get_context()
    df=ctx["df"]; th=ctx["th"]; T=ctx["T"]

    col_b, col_img = st.columns([2,1])
    with col_b:
        banner(IMAGES["kpi_banner"], 185,
               f"{T['bloc2_label']} · {ctx['scope_label']}",
               T["bloc2_chart1_title"], th, accent=th["blue"], tint_hex="#0ea5e9", tint_strength=0.30)
    with col_img:
        img_card(IMAGES["kpi_side"], 185, "Pollution", "PM2.5 · Smog", th,
                 tint_hex="#0ea5e9", tint_strength=0.28)

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

    c1,c2 = st.columns(2)
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
                       font=dict(color=th["text"],size=13)))
        fig1.update_xaxes(**GRID); fig1.update_yaxes(**GRID)
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(x=df["IRS"], nbinsx=40,
            marker_color=th["teal"], opacity=0.78))
        for pv,lb,lc in [(float(ctx["p50"]),f"p50={ctx['p50']:.3f}",th["green"]),
                         (float(ctx["p75"]),f"p75={ctx['p75']:.3f}",th["amber"]),
                         (float(ctx["p90"]),f"p90={ctx['p90']:.3f}",th["red"])]:
            fig2.add_vline(x=pv, line=dict(color=lc,width=1.5,dash="dot"),
                annotation_text=lb, annotation_font_color=lc, annotation_font_size=10)
        fig2.update_layout(**PL, height=260, showlegend=False,
            title=dict(text=f"{T['bloc2_chart2_title']} · {ctx['scope_label']}",
                       font=dict(color=th["text"],size=13)))
        fig2.update_xaxes(**GRID); fig2.update_yaxes(**GRID)
        st.plotly_chart(fig2, use_container_width=True)

    sources_bar(f"{T['sources_who']}", th)
