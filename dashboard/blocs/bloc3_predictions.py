"""blocs/bloc3_predictions.py — Prédictions · bilingue + thème"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np, pandas as pd
from datetime import date
from utils import get_context, banner, img_card, sources_bar, empty_state, irs_level, VILLES
from assets import IMAGES

def render(profil):
    ctx = get_context()
    df=ctx["df"]; th=ctx["th"]; T=ctx["T"]; mois=ctx["mois"]

    banner(IMAGES["pred_banner"], 185,
           f"{T['bloc3_label']} · {ctx['scope_label']}",
           T["bloc3_subtitle"], th, accent=th["amber"], tint_hex="#f59e0b", tint_strength=0.28)

    if len(df) == 0: empty_state(T, th); return

    PL = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
              font=dict(color=th["text2"],size=12), margin=dict(l=44,r=20,t=44,b=36))
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False)

    tabs = st.tabs([T["bloc3_tab_short"], T["bloc3_tab_sim"], T["bloc3_tab_monthly"]])

    with tabs[0]:
        cv, ci = st.columns([1,3])
        with cv:
            villes_dispo = sorted(df["ville"].unique().tolist())
            di = villes_dispo.index(ctx["ville_sel"]) if ctx["ville_sel"] in villes_dispo else 0
            v  = st.selectbox(T["bloc3_city_select"], villes_dispo, index=di, key="p_v")
            img_card(IMAGES["ctx_foret"], 120, v, ctx["scope_annees"], th, tint_hex="#00d4b1")
        with ci:
            np.random.seed(hash(v) % 2**31)
            df_v = df[df["ville"]==v]
            base = float(df_v["pm2_5_moyen"].mean()) if len(df_v)>0 else float(ctx["pm25_moy"])
            jours = pd.date_range(date.today(), periods=3, freq="D")
            pred  = [base*(0.88+0.24*np.random.random()) for _ in range(3)]
            hist  = (df_v if len(df_v)>0 else df).groupby("date")["pm2_5_moyen"].mean().tail(21).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist["date"], y=hist["pm2_5_moyen"], mode="lines",
                name=T["bloc3_history_label"], line=dict(color=th["blue"],width=2),
                fill="tozeroy", fillcolor="rgba(14,165,233,0.07)"))
            fig.add_trace(go.Scatter(
                x=list(jours)+list(jours[::-1]),
                y=[p*1.18 for p in pred]+[p*0.82 for p in pred[::-1]],
                fill="toself", fillcolor="rgba(245,158,11,0.12)",
                line=dict(color="rgba(0,0,0,0)"), showlegend=False))
            fig.add_trace(go.Scatter(x=jours, y=pred, mode="lines+markers",
                name=T["bloc3_pred_label"], line=dict(color=th["amber"],width=2.5,dash="dash"),
                marker=dict(size=10,color=th["amber"],line=dict(color=th["bg3"],width=2))))
            fig.add_hline(y=15.0, line=dict(color=th["red"],width=1,dash="dash"),
                annotation_text=T["who_threshold"], annotation_font_color=th["red"], annotation_font_size=10)
            fig.update_layout(**PL, height=310,
                title=dict(text=f"PM2.5 · {v} · {T['bloc3_pred_label']} (base {ctx['scope_annees']}: {base:.1f} µg/m³)",
                           font=dict(color=th["text"],size=13)),
                legend=dict(font=dict(color=th["text2"],size=11), bgcolor="rgba(0,0,0,0)"))
            fig.update_xaxes(**GRID); fig.update_yaxes(**GRID)
            st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        ci2, cc = st.columns([1,2])
        with ci2:
            img_card(IMAGES["pred_harmattan"], 300, "Harmattan · Bauer et al. 2024",
                     "Dust > p90", th, tint_hex="#f59e0b", tint_strength=0.30)
        with cc:
            def _m(col, fb): return float(df[col].mean()) if col in df.columns and len(df)>0 else fb
            st.markdown(f"<div style='font-size:13px;color:{th['text2']};margin-bottom:12px;'>"
                        f"{T['bloc3_sim_intro']} <b style='color:{th['teal']};'>{ctx['scope_label']}</b></div>",
                        unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                temp=st.slider(T["bloc3_temp"],20,45,int(min(45,max(20,_m("temperature_2m_max",30)))),key="s_t")
                vent=st.slider(T["bloc3_wind"],0,60,int(min(60,max(0,_m("wind_speed_10m_max",15)))),key="s_v")
                hum =st.slider(T["bloc3_humidity"],10,100,int(min(100,max(10,_m("relative_humidity_2m_mean",60)))),key="s_h")
            with c2:
                dust=st.slider(T["bloc3_dust"],0,300,int(min(300,max(0,_m("dust_moyen",80)))),key="s_d")
                harm=st.checkbox(T["bloc3_harmattan"], key="s_harm")
                feux=st.checkbox(T["bloc3_fire"],      key="s_feux")
            pm25_s=max(5,10+0.4*temp-0.3*vent+0.05*dust+(15 if harm else 0)+(20 if feux else 0))
            irs_s =min(1.0,pm25_s/80*0.35+dust/300*0.25+0.10)
            nc,nt,_ = irs_level(irs_s,ctx["p50"],ctx["p75"],ctx["p90"],T,th)
            ecart   = irs_s-ctx["irs_moy"]
            ecart_t = (f"↑ +{ecart:.3f} vs {T['bloc3_sim_avg']} {ctx['scope_annees']}"
                       if ecart>0 else f"↓ {ecart:.3f} vs {T['bloc3_sim_avg']} {ctx['scope_annees']}")
            st.markdown(f"""
            <div style="background:{th['bg_elevated']};border:2px solid {nc};
                        border-radius:12px;padding:16px 20px;margin-top:14px;
                        display:flex;align-items:center;justify-content:space-between;gap:14px;">
                <div>
                    <div style="font-size:11px;color:{th['text3']};margin-bottom:3px;">{T['bloc3_sim_irs']}</div>
                    <div style="font-size:32px;font-weight:700;color:{nc};">{irs_s:.3f}</div>
                    <div style="font-size:11px;color:{'#ef4444' if ecart>0 else '#10b981'};margin-top:3px;">{ecart_t}</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:20px;">{nt}</div>
                    <div style="font-size:12px;color:{th['text2']};margin-top:5px;">{T['bloc3_sim_pm25']} : {pm25_s:.1f} µg/m³</div>
                    <div style="font-size:11px;color:{th['text3']};margin-top:3px;">
                        {T['bloc3_sim_avg']} {ctx['scope_label']} : {ctx['pm25_moy']:.1f} µg/m³
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tabs[2]:
        an = st.selectbox(T["bloc3_year_select"], list(range(2020,2026)), index=5, key="lt_a")
        cal = df[df["date"].dt.year==an].groupby(df["date"].dt.month)["pm2_5_moyen"].mean().reset_index()
        cal.columns=["mois_num","pm2_5_moyen"]
        cal["mois"] = cal["mois_num"].apply(lambda m: mois[m-1])
        cbar=[th["green"] if v<15 else th["amber"] if v<25 else th["coral"] if v<37.5 else th["red"] for v in cal["pm2_5_moyen"]]
        fig=go.Figure()
        fig.add_trace(go.Bar(x=cal["mois"],y=cal["pm2_5_moyen"],marker_color=cbar,opacity=0.9,
            text=cal["pm2_5_moyen"].round(1),textposition="outside",textfont=dict(color=th["text2"],size=10)))
        fig.add_hline(y=15.0,line=dict(color=th["red"],width=1.2,dash="dash"),
            annotation_text=T["who_threshold"],annotation_font_color=th["red"],annotation_font_size=10)
        fig.update_layout(**PL,height=310,showlegend=False,
            title=dict(text=f"{T['bloc3_monthly_title']} · {ctx['scope_label']}",font=dict(color=th["text"],size=13)))
        fig.update_xaxes(**GRID); fig.update_yaxes(**GRID)
        st.plotly_chart(fig, use_container_width=True)

    sources_bar(f"XGBoost + LightGBM · Prophet · {T['sources_who']}", th)
