"""blocs/bloc6_contexte.py — Contexte · bilingue + thème"""
import streamlit as st
import plotly.graph_objects as go
from utils import get_context, banner, season_card, sources_bar, empty_state
from assets import IMAGES

def render(profil):
    ctx = get_context()
    df=ctx["df"]; th=ctx["th"]; T=ctx["T"]; mois=ctx["mois"]

    banner(IMAGES["ctx_foret"], 190,
           f"{T['bloc6_label']} · {ctx['scope_label']}",
           T["bloc6_subtitle"], th, accent=th["gray"], tint_hex="#0ea5e9", tint_strength=0.22)

    if len(df) == 0: empty_state(T, th); return

    PL = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor=th["plot_bg"],
              font=dict(color=th["text2"],size=12),margin=dict(l=44,r=20,t=44,b=36))
    GRID = dict(gridcolor=th["grid_color"],linecolor=th["line_color"],zeroline=False)

    c1,c2,c3 = st.columns(3)
    with c1:
        pdom = df["polluant_dominant"].value_counts()
        fig  = go.Figure(go.Pie(labels=pdom.index,values=pdom.values,hole=0.55,
            marker=dict(colors=[th["blue"],th["amber"],th["teal"],th["coral"],th["purple"]]),
            textfont=dict(color=th["text2"],size=11)))
        fig.update_layout(**PL,height=240,showlegend=True,
            title=dict(text=f"{T['bloc6_chart1_title']} · {ctx['scope_annees']}",font=dict(color=th["text"],size=13)),
            legend=dict(font=dict(color=th["text2"],size=10),bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, width="stretch")
    with c2:
        df_brut=ctx["df_brut"]
        villes_sel  = st.session_state.get("ville_sel_list",  "ALL")
        regions_sel = st.session_state.get("region_sel_list", "ALL")
        def _men(an):
            d=df_brut[df_brut["date"].dt.year==an]
            if villes_sel  != "ALL" and isinstance(villes_sel,  list): d=d[d["ville"].isin(villes_sel)]
            if regions_sel != "ALL" and isinstance(regions_sel, list): d=d[d["region"].isin(regions_sel)]
            return d.groupby(d["date"].dt.month)["pm2_5_moyen"].mean()
        m_fin =_men(ctx["an_max"]); m_prec=_men(ctx["an_max"]-1)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=mois,y=m_prec.reindex(range(1,13)).values,mode="lines",
            name=str(ctx["an_max"]-1),line=dict(color=th["gray"],width=1.5,dash="dot")))
        fig.add_trace(go.Scatter(x=mois,y=m_fin.reindex(range(1,13)).values,mode="lines+markers",
            name=str(ctx["an_max"]),line=dict(color=th["blue"],width=2),marker=dict(size=5)))
        fig.update_layout(**PL,height=240,
            title=dict(text=T["bloc6_chart2_prefix"].format(y1=ctx["an_max"]-1,y2=ctx["an_max"])+
                       f" · {ctx['scope_ville']}",font=dict(color=th["text"],size=13)),
            legend=dict(font=dict(color=th["text2"],size=11),bgcolor="rgba(0,0,0,0)"))
        fig.update_xaxes(**GRID); fig.update_yaxes(**GRID)
        st.plotly_chart(fig, width="stretch")
    with c3:
        eps={"Zone sahélienne":[42,28,35],"Zone équatoriale":[8,12,15],"Zone côtière":[5,8,10],"Zone montagne":[15,10,8],"Zone savane":[25,20,22]}
        zones=list(eps.keys())
        fig=go.Figure()
        for vals,nom,color in [([v[0] for v in eps.values()],T["bloc6_harmattan_label"],th["amber"]),
                               ([v[1] for v in eps.values()],T["bloc6_fire_label"],th["red"]),
                               ([v[2] for v in eps.values()],T["bloc6_heat_label"],th["coral"])]:
            fig.add_trace(go.Bar(x=vals,y=zones,orientation="h",name=nom,marker_color=color,opacity=0.85))
        fig.update_layout(**PL,height=240,barmode="group",
            title=dict(text=T["bloc6_chart3_title"],font=dict(color=th["text"],size=13)),
            legend=dict(font=dict(color=th["text2"],size=10),bgcolor="rgba(0,0,0,0)"))
        fig.update_xaxes(**GRID); fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")

    st.markdown(f"<div style='font-size:12px;font-weight:500;color:{th['text']};margin:16px 0 12px;'>"
                f"{T['bloc6_seasons_title']}</div>", unsafe_allow_html=True)

    saisons = [
        (IMAGES["ctx_harmattan"], T["season1_periode"], T["season1_titre"], T["season1_detail"], th["amber"]),
        (IMAGES["ctx_pluies"],    T["season2_periode"], T["season2_titre"], T["season2_detail"], th["blue"]),
        (IMAGES["ctx_foret"],     T["season3_periode"], T["season3_titre"], T["season3_detail"], th["teal"]),
        (IMAGES["ctx_feux"],      T["season4_periode"], T["season4_titre"], T["season4_detail"], th["coral"]),
    ]
    scols = st.columns(4)
    for col,s in zip(scols,saisons):
        with col: season_card(s[0],s[1],s[2],s[3],s[4],th)

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    uv_m    = df.groupby(df["date"].dt.month)["uv_moyen"].mean()
    ozone_m = df.groupby(df["date"].dt.month)["ozone_moyen"].mean()
    fig_uv  = go.Figure()
    fig_uv.add_trace(go.Scatter(x=mois,y=uv_m.reindex(range(1,13)).values,
        mode="lines+markers",name="UV index",line=dict(color=th["amber"],width=2),
        marker=dict(size=5),yaxis="y"))
    fig_uv.add_trace(go.Scatter(x=mois,y=ozone_m.reindex(range(1,13)).values,
        mode="lines+markers",name="Ozone µg/m³",line=dict(color=th["purple"],width=2),
        marker=dict(size=5),yaxis="y2"))
    fig_uv.update_layout(**PL,height=250,
        title=dict(text=f"{T['bloc6_uv_title']} · {ctx['scope_label']}",font=dict(color=th["text"],size=13)),
        legend=dict(font=dict(color=th["text2"],size=11),bgcolor="rgba(0,0,0,0)"),
        yaxis2=dict(title="Ozone µg/m³",overlaying="y",side="right",gridcolor="rgba(0,0,0,0)"))
    fig_uv.update_xaxes(**GRID)
    fig_uv.update_yaxes(title_text="UV index",**GRID)
    st.plotly_chart(fig_uv, width="stretch")

    sources_bar(f"{T['sources_cecc']} · {T['sources_bauer']} · {T['sources_barker']} · {T['sources_who']}", th)
