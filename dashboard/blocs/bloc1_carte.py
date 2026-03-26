"""blocs/bloc1_carte.py — Carte + analyses PM2.5 enrichies"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils import get_context, banner, img_card, sources_bar, empty_state, COORDS
from assets import IMAGES

# Polluants avec seuils OMS et couleurs
POLLUANTS = [
    {"col":"pm2_5_moyen", "nom_fr":"PM2.5",  "nom_en":"PM2.5",  "seuil":15,   "unite":"µg/m³", "color":"#f87171"},
    {"col":"pm10_moyen",  "nom_fr":"PM10",   "nom_en":"PM10",   "seuil":45,   "unite":"µg/m³", "color":"#fb923c"},
    {"col":"no2_moyen",   "nom_fr":"NO₂",    "nom_en":"NO₂",    "seuil":25,   "unite":"µg/m³", "color":"#fbbf24"},
    {"col":"so2_moyen",   "nom_fr":"SO₂",    "nom_en":"SO₂",    "seuil":40,   "unite":"µg/m³", "color":"#a78bfa"},
    {"col":"ozone_moyen", "nom_fr":"Ozone",  "nom_en":"Ozone",  "seuil":100,  "unite":"µg/m³", "color":"#38bdf8"},
    {"col":"co_moyen",    "nom_fr":"CO",     "nom_en":"CO",     "seuil":0.6,  "unite":"mg/m³", "color":"#34d399"},
]

def _risk_color(val, seuil, th):
    if val <= seuil:             return th["green"]
    if val <= seuil * 1.5:      return th["amber"]
    if val <= seuil * 2.5:      return th["coral"]
    return                             th["red"]

def render(profil):
    ctx = get_context()
    df = ctx["df"]; th = ctx["th"]; T = ctx["T"]; lang = ctx["lang"]

    banner(IMAGES["carte_banner"], 190,
           f"{T['bloc1_label']} · {ctx['scope_label']}",
           T["bloc1_subtitle"], th,
           accent=th["teal"], tint_hex="#00d4b1", tint_strength=0.32)

    if len(df) == 0:
        empty_state(T, th)
        return

    agg = df.groupby("ville")[["pm2_5_moyen","IRS"]].mean().reset_index()
    agg["lat"] = agg["ville"].map(lambda v: COORDS.get(v,(4.0,12.0))[0])
    agg["lon"] = agg["ville"].map(lambda v: COORDS.get(v,(4.0,12.0))[1])

    PL   = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
                font=dict(color=th["text2"], size=12), margin=dict(l=44,r=20,t=44,b=36))
    GRID = dict(gridcolor=th["grid_color"], linecolor=th["line_color"], zeroline=False)

    # ══ CARTE ════════════════════════════════════════════════════════════════
    col_map, col_side = st.columns([3, 1])
    with col_map:
        fig = go.Figure()
        if ctx["ville_sel"] not in ("(Toutes)","(All)"):
            autres = agg[agg["ville"] != ctx["ville_sel"]]
            sel    = agg[agg["ville"] == ctx["ville_sel"]]
            if len(autres) > 0:
                fig.add_trace(go.Scattergeo(
                    lat=autres["lat"], lon=autres["lon"], mode="markers",
                    marker=dict(size=8, color="rgba(107,122,150,0.35)",
                                line=dict(width=0.5,color="rgba(255,255,255,0.08)")),
                    hoverinfo="skip", showlegend=False))
            if len(sel) > 0:
                fig.add_trace(go.Scattergeo(
                    lat=sel["lat"], lon=sel["lon"], mode="markers+text",
                    marker=dict(size=24, color=sel["pm2_5_moyen"],
                        colorscale=[[0,th["green"]],[0.4,th["amber"]],[0.7,th["coral"]],[1,th["red"]]],
                        cmin=5, cmax=80, colorbar=dict(title="PM2.5",thickness=12),
                        line=dict(width=2.5,color=th["teal"])),
                    text=sel["ville"], textposition="top center",
                    textfont=dict(size=13,color=th["teal"]),
                    hovertemplate="<b>%{text}</b><br>PM2.5 : %{marker.color:.1f} µg/m³<extra></extra>"))
                geo_center = dict(lat=float(sel["lat"].values[0]),lon=float(sel["lon"].values[0]))
                geo_scale = 28
        else:
            fig.add_trace(go.Scattergeo(
                lat=agg["lat"], lon=agg["lon"], mode="markers+text",
                marker=dict(size=agg["pm2_5_moyen"].clip(8,30), color=agg["pm2_5_moyen"],
                    colorscale=[[0,th["green"]],[0.4,th["amber"]],[0.7,th["coral"]],[1,th["red"]]],
                    cmin=5, cmax=80, colorbar=dict(title="PM2.5 µg/m³",thickness=12),
                    line=dict(width=0.5,color="rgba(255,255,255,0.2)")),
                text=agg["ville"], textposition="top center",
                textfont=dict(size=9,color=th["text2"]),
                hovertemplate="<b>%{text}</b><br>PM2.5 : %{marker.color:.1f} µg/m³<br>IRS : %{customdata:.3f}<extra></extra>",
                customdata=agg["IRS"]))
            geo_center = dict(lat=5.5,lon=12.3); geo_scale=12

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=th["plot_bg"],
            font=dict(color=th["text2"],size=12), margin=dict(l=10,r=10,t=44,b=10),
            height=380,
            title=dict(text=f"{T['bloc1_map_title']} · {ctx['scope_label']}",
                       font=dict(color=th["text"],size=14)),
            geo=dict(scope="africa", center=geo_center, projection_scale=geo_scale,
                     showland=True, landcolor=th["bg_tertiary"],
                     showocean=True, oceancolor=th["bg_primary"] if th["name"]=="dark" else "#c8e6fa",
                     showcountries=True, countrycolor=th["border_soft"],
                     showframe=False, bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

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
            {"".join([f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:6px;">'
                f'<div style="width:9px;height:9px;border-radius:50%;background:{co};flex-shrink:0;"></div>'
                f'<div><div style="font-size:10px;color:{th["text"]};">{va}</div>'
                f'<div style="font-size:9px;color:{th["text3"]};">{la}</div></div></div>'
                for co,va,la in [(th["green"],"< 15 µg/m³",T["bloc1_oms_conform"]),
                                 (th["amber"],"15–25",""),
                                 (th["coral"],"25–37.5","IT3"),
                                 (th["red"],"> 37.5","")]])}
        </div>
        <div style="background:rgba(239,68,68,0.10);border:1px solid rgba(239,68,68,0.22);
                    border-radius:10px;padding:12px;margin-top:8px;text-align:center;">
            <div style="font-size:26px;font-weight:600;color:{th['red']};">{n_dep}</div>
            <div style="font-size:10px;color:{th['text2']};">{T['bloc1_cities_above']}</div>
            <div style="font-size:9px;color:{th['text3']};margin-top:2px;">
                {pct} · {T['bloc1_period']} {ctx['scope_annees']}
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(99,160,255,0.10);margin:24px 0 20px;'>", unsafe_allow_html=True)

    # ══ ANALYSES ENRICHIES ════════════════════════════════════════════════════
    # Titre section
    titre_analyses = "Analyses détaillées · " + ctx["scope_label"]
    st.markdown(f"""
    <div style="font-size:16px;font-weight:600;color:{th['text']};margin-bottom:18px;">
        📊 {titre_analyses}
    </div>""", unsafe_allow_html=True)

    # ── Ligne 1 : PM2.5 par région + Tendance 12 mois ─────────────────────────
    ca, cb = st.columns(2)

    with ca:
        # PM2.5 par région
        lbl = "PM2.5 moyen par région" if lang=="fr" else "Avg PM2.5 by region"
        pm_reg = df.groupby("region")["pm2_5_moyen"].mean().sort_values(ascending=True)
        colors = [_risk_color(v, 15, th) for v in pm_reg.values]
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            x=pm_reg.values, y=pm_reg.index, orientation="h",
            marker_color=colors, opacity=0.88,
            text=[f"{v:.1f}" for v in pm_reg.values],
            textposition="outside", textfont=dict(color=th["text2"],size=10)))
        fig_reg.add_vline(x=15, line=dict(color=th["red"],width=1.2,dash="dash"),
            annotation_text="OMS 15", annotation_font_color=th["red"],annotation_font_size=10)
        fig_reg.update_layout(**PL, height=300, showlegend=False,
            title=dict(text=lbl, font=dict(color=th["text"],size=13)))
        fig_reg.update_xaxes(**GRID); fig_reg.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_reg, use_container_width=True)

    with cb:
        # Tendance PM2.5 sur les 12 derniers mois
        lbl2 = "Tendance PM2.5 · 12 derniers mois" if lang=="fr" else "PM2.5 trend · Last 12 months"
        df_sorted = df.sort_values("date")
        df_last12 = df_sorted[df_sorted["date"] >= df_sorted["date"].max() - np.timedelta64(365,"D")]
        tend_men = df_last12.groupby(df_last12["date"].dt.to_period("M"))["pm2_5_moyen"].mean().reset_index()
        tend_men["date"] = tend_men["date"].dt.to_timestamp()
        fig_tend = go.Figure()
        fig_tend.add_trace(go.Scatter(
            x=tend_men["date"], y=tend_men["pm2_5_moyen"], mode="lines+markers",
            line=dict(color=th["blue"],width=2),
            marker=dict(size=6,color=th["blue"],line=dict(color=th["bg3"],width=1.5)),
            fill="tozeroy", fillcolor="rgba(14,165,233,0.07)"))
        fig_tend.add_hline(y=15, line=dict(color=th["red"],width=1,dash="dash"),
            annotation_text="OMS", annotation_font_color=th["red"],annotation_font_size=10)
        fig_tend.update_layout(**PL, height=300, showlegend=False,
            title=dict(text=lbl2, font=dict(color=th["text"],size=13)))
        fig_tend.update_xaxes(**GRID); fig_tend.update_yaxes(**GRID)
        st.plotly_chart(fig_tend, use_container_width=True)

    # ── Ligne 2 : Top 3 polluants + Top 5 villes critiques ───────────────────
    cc, cd = st.columns(2)

    with cc:
        # Top 3 polluants dominants
        lbl3 = "Top 3 polluants dominants · National" if lang=="fr" else "Top 3 dominant pollutants · National"
        if "polluant_dominant" in df.columns:
            top3 = df["polluant_dominant"].value_counts().head(3)
            total = top3.sum()
            st.markdown(f"""
            <div style="background:{th['bg_tertiary']};border:1px solid {th['border_soft']};
                        border-radius:12px;padding:16px 18px;height:300px;box-sizing:border-box;">
                <div style="font-size:13px;font-weight:500;color:{th['text']};margin-bottom:14px;">
                    🏆 {lbl3}
                </div>""", unsafe_allow_html=True)
            medal_colors = [th["amber"], th["gray"], th["coral"]]
            medals = ["🥇","🥈","🥉"]
            for i,(poll,cnt) in enumerate(top3.items()):
                pct_v = cnt/total*100 if total>0 else 0
                mc = medal_colors[i] if i < len(medal_colors) else th["blue"]
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                    <div style="font-size:20px;">{medals[i]}</div>
                    <div style="flex:1;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                            <span style="font-size:13px;color:{th['text']};font-weight:500;">{poll}</span>
                            <span style="font-size:12px;color:{mc};font-weight:600;">{pct_v:.0f}%</span>
                        </div>
                        <div style="background:{th['bg_elevated']};border-radius:4px;height:6px;overflow:hidden;">
                            <div style="background:{mc};height:100%;width:{pct_v:.0f}%;border-radius:4px;"></div>
                        </div>
                        <div style="font-size:10px;color:{th['text3']};margin-top:2px;">
                            {cnt:,} {'jours' if lang=='fr' else 'days'}
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with cd:
        # Top 5 villes en alerte critique
        lbl4 = "Top 5 villes · Alerte critique IRS" if lang=="fr" else "Top 5 cities · Critical HRI alert"
        df["niv_num"] = np.searchsorted([ctx["p50"],ctx["p75"],ctx["p90"]],df["IRS"].values,side="right").clip(0,3)
        crit_v = (df[df["niv_num"]==3].groupby("ville").size()
                    .sort_values(ascending=False).head(5).reset_index())
        crit_v.columns = ["ville","n_jours"]
        max_j = crit_v["n_jours"].max() if len(crit_v)>0 else 1
        st.markdown(f"""
        <div style="background:{th['bg_tertiary']};border:1px solid rgba(239,68,68,0.25);
                    border-radius:12px;padding:16px 18px;height:300px;box-sizing:border-box;">
            <div style="font-size:13px;font-weight:500;color:{th['red']};margin-bottom:14px;">
                🚨 {lbl4}
            </div>""", unsafe_allow_html=True)
        if len(crit_v) == 0:
            st.markdown(f"<div style='font-size:12px;color:{th['text3']};'>Aucune ville en alerte critique sur la période.</div>", unsafe_allow_html=True)
        for _, row in crit_v.iterrows():
            pct_v = row["n_jours"]/max_j*100
            st.markdown(f"""
            <div style="margin-bottom:11px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                    <span style="font-size:12px;color:{th['text']};font-weight:500;">📍 {row['ville']}</span>
                    <span style="font-size:11px;color:{th['red']};font-weight:600;">
                        {row['n_jours']} {'j' if lang=='fr' else 'd'}
                    </span>
                </div>
                <div style="background:{th['bg_elevated']};border-radius:4px;height:6px;overflow:hidden;">
                    <div style="background:linear-gradient(to right,{th['coral']},{th['red']});
                                height:100%;width:{pct_v:.0f}%;border-radius:4px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Ligne 3 : Épisodes climatiques + Tableau polluants OMS ───────────────
    ce, cf = st.columns(2)

    with ce:
        # Épisodes climatiques par zone
        lbl5 = "Épisodes climatiques par zone (p90)" if lang=="fr" else "Climate episodes by zone (p90)"
        eps = {"Zone sahélienne":[42,28,35],"Zone équatoriale":[8,12,15],
               "Zone côtière":[5,8,10],"Zone montagne":[15,10,8],"Zone savane":[25,20,22]}
        zones = list(eps.keys())
        lbl_h = "Harmattan" if lang=="fr" else "Harmattan"
        lbl_f = "Feux"      if lang=="fr" else "Fires"
        lbl_c = "Chaleur"   if lang=="fr" else "Heat"
        fig_ep = go.Figure()
        for vals,nom,color in [([v[0] for v in eps.values()],lbl_h,th["amber"]),
                               ([v[1] for v in eps.values()],lbl_f,th["red"]),
                               ([v[2] for v in eps.values()],lbl_c,th["coral"])]:
            fig_ep.add_trace(go.Bar(x=vals,y=zones,orientation="h",name=nom,
                                    marker_color=color,opacity=0.85))
        fig_ep.update_layout(**PL, height=300, barmode="group",
            title=dict(text=lbl5, font=dict(color=th["text"],size=13)),
            legend=dict(font=dict(color=th["text2"],size=10),bgcolor="rgba(0,0,0,0)"))
        fig_ep.update_xaxes(**GRID); fig_ep.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_ep, use_container_width=True)

    with cf:
        # Tableau tous les polluants
        lbl6 = "Concentrations moyennes · Seuils OMS" if lang=="fr" else "Average concentrations · WHO thresholds"
        st.markdown(f"""
        <div style="background:{th['bg_tertiary']};border:1px solid {th['border_soft']};
                    border-radius:12px;padding:16px 18px;height:300px;
                    box-sizing:border-box;overflow-y:auto;">
            <div style="font-size:13px;font-weight:500;color:{th['text']};margin-bottom:12px;">
                ⚗️ {lbl6}
            </div>""", unsafe_allow_html=True)

        hdr_conc  = "Concentration" if lang=="fr" else "Concentration"
        hdr_seuil = "Seuil OMS"     if lang=="fr" else "WHO Threshold"
        hdr_risk  = "Risque"        if lang=="fr" else "Risk"

        # En-tête
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:60px 1fr 80px 70px 60px;
                    gap:6px;padding:6px 0;border-bottom:1px solid {th['border_soft']};
                    font-size:10px;color:{th['text3']};text-transform:uppercase;letter-spacing:.06em;">
            <div></div><div>Polluant</div>
            <div style="text-align:right;">{hdr_conc}</div>
            <div style="text-align:right;">{hdr_seuil}</div>
            <div style="text-align:center;">{hdr_risk}</div>
        </div>""", unsafe_allow_html=True)

        for p in POLLUANTS:
            if p["col"] not in df.columns:
                continue
            moy = float(df[p["col"]].mean())
            rc  = _risk_color(moy, p["seuil"], th)
            ok  = moy <= p["seuil"]
            badge = f"✅" if ok else ("⚠️" if moy<=p["seuil"]*1.5 else "🔴")
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:60px 1fr 80px 70px 60px;
                        gap:6px;padding:7px 0;border-bottom:1px solid {th['border_soft']}22;
                        align-items:center;">
                <div style="width:10px;height:10px;border-radius:50%;
                            background:{p['color']};margin:0 auto;"></div>
                <div style="font-size:12px;font-weight:500;color:{th['text']};">{p['nom_fr' if lang=='fr' else 'nom_en']}</div>
                <div style="font-size:12px;color:{rc};font-weight:600;text-align:right;
                            font-family:'DM Mono',monospace;">{moy:.1f} {p['unite']}</div>
                <div style="font-size:11px;color:{th['text3']};text-align:right;
                            font-family:'DM Mono',monospace;">{p['seuil']} {p['unite']}</div>
                <div style="font-size:14px;text-align:center;">{badge}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    sources_bar(f"{T['sources_who']} · {T['sources_cecc']} · {T['sources_bauer']}", th)
