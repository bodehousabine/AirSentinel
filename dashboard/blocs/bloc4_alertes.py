"""blocs/bloc4_alertes.py — Alertes · bilingue + thème"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils import get_context, sources_bar, empty_state
from assets import IMAGES

def _nk(irs, p50, p75, p90):
    if irs<p50: return "faible"
    if irs<p75: return "modere"
    if irs<p90: return "eleve"
    return "critique"

def _msg(profil_key, nk, T, ctx, th):
    key = f"bloc4_msg_{nk}_{profil_key}"
    txt = T.get(key, "—")
    if nk in ("faible","modere") and profil_key == "researcher":
        txt += f" · {ctx['scope_label']}"
    return txt

def render(profil):
    ctx = get_context()
    df=ctx["df"]; th=ctx["th"]; T=ctx["T"]

    # Bannière duo images
    cb1,cb2 = st.columns(2)
    for col,img,title,sub,ac,brd in [
        (cb1,IMAGES["alert_feux"],   T["bloc4_feux_title"],   T["bloc4_feux_sub"],   th["red"],  "rgba(239,68,68,0.22)"),
        (cb2,IMAGES["alert_chaleur"],T["bloc4_chaleur_title"],T["bloc4_chaleur_sub"],th["amber"],"rgba(245,158,11,0.22)"),
    ]:
        with col:
            st.markdown(f"""
            <div style="position:relative;border-radius:12px;overflow:hidden;height:155px;
                        margin-bottom:16px;border:1px solid {brd};">
                <img src="{img}" style="width:100%;height:100%;object-fit:cover;
                           filter:saturate(0.65) brightness(0.50);"
                     onerror="this.style.opacity='0'"/>
                <div style="position:absolute;inset:0;background:linear-gradient(to top,
                            rgba(2,12,24,0.90),transparent 60%);"></div>
                <div style="position:absolute;bottom:0;left:0;right:0;padding:12px 16px;">
                    <div style="font-size:17px;font-weight:600;color:#e0f2fe;">{title}</div>
                    <div style="font-size:11px;color:{ac};margin-top:2px;">{sub}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    # Sous-titre
    st.markdown(
        f"<div style='font-size:13px;color:{th['text2']};margin-bottom:16px;'>"
        f"{T['bloc4_label']} · <b style='color:{th['text']};'>{ctx['scope_label']}</b> · "
        f"IRS : <b style='color:{ctx['irs_color']};'>{ctx['irs_moy']:.3f} — {ctx['irs_label']}</b>"
        f" · {profil}</div>",
        unsafe_allow_html=True,
    )
    if len(df) == 0: empty_state(T, th); return

    # Mapping profil → clé
    profil_map = {
        T["sidebar_profile_citizen"]:    "citizen",
        T["sidebar_profile_health"]:     "health",
        T["sidebar_profile_mayor"]:      "mayor",
        T["sidebar_profile_researcher"]: "researcher",
    }
    pk = profil_map.get(profil, "citizen")

    niveaux = [
        {"nk":"faible",   "icon":"🟢","lbl":T["level_faible"],   "c":th["green"],"bg":"rgba(16,185,129,0.07)","brd":"rgba(16,185,129,0.25)"},
        {"nk":"modere",   "icon":"🟡","lbl":T["level_modere"],   "c":th["amber"],"bg":"rgba(245,158,11,0.07)","brd":"rgba(245,158,11,0.25)"},
        {"nk":"eleve",    "icon":"🟠","lbl":T["level_eleve"],    "c":th["coral"],"bg":"rgba(249,115,22,0.07)","brd":"rgba(249,115,22,0.28)"},
        {"nk":"critique", "icon":"🔴","lbl":T["level_critique"], "c":th["red"],  "bg":"rgba(239,68,68,0.08)", "brd":"rgba(239,68,68,0.32)"},
    ]
    seuils = [f"IRS < {ctx['p50']:.3f}",
              f"{ctx['p50']:.3f} → {ctx['p75']:.3f}",
              f"{ctx['p75']:.3f} → {ctx['p90']:.3f}",
              f"≥ {ctx['p90']:.3f}"]

    cols = st.columns(4)
    for i,(niv,seuil) in enumerate(zip(niveaux,seuils)):
        msg   = _msg(pk, niv["nk"], T, ctx, th)
        actif = (niv["nk"] == ctx["irs_nk"])
        brd   = f"2px solid {niv['c']}" if actif else f"1px solid {niv['brd']}"
        badge = (f'<span style="font-size:10px;background:{niv["c"]}22;border-radius:4px;'
                 f'padding:2px 7px;margin-left:6px;color:{niv["c"]};">{T["bloc4_current_badge"]}</span>') if actif else ""
        with cols[i]:
            st.markdown(f"""
            <div style="background:{niv['bg']};border:{brd};border-radius:12px;
                        padding:18px 14px;height:220px;display:flex;flex-direction:column;">
                <div style="font-size:26px;margin-bottom:7px;">{niv['icon']}</div>
                <div style="font-size:13px;font-weight:600;color:{niv['c']};
                            letter-spacing:.05em;margin-bottom:3px;">{niv['lbl']}{badge}</div>
                <div style="font-size:10px;color:{th['text3']};font-family:'DM Mono',monospace;
                            margin-bottom:10px;">{seuil}</div>
                <div style="font-size:12px;color:{th['text']};line-height:1.55;flex:1;">{msg}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

    df2 = df.copy()
    df2["niv_num"] = np.searchsorted([ctx["p50"],ctx["p75"],ctx["p90"]],df2["IRS"].values,side="right").clip(0,3)
    hn = (df2.groupby([df2["date"].dt.year,"niv_num"]).size()
             .unstack(fill_value=0).reindex(columns=[0,1,2,3],fill_value=0))
    hn.columns = [T["level_faible"],T["level_modere"],T["level_eleve"],T["level_critique"]]
    PL = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor=th["plot_bg"],
              font=dict(color=th["text2"],size=12),margin=dict(l=44,r=20,t=44,b=36))
    GRID = dict(gridcolor=th["grid_color"],linecolor=th["line_color"],zeroline=False)
    fig = go.Figure()
    for col,pc in zip(hn.columns,[th["green"],th["amber"],th["coral"],th["red"]]):
        fig.add_trace(go.Bar(x=hn.index,y=hn[col],name=col,marker_color=pc,opacity=0.85))
    fig.update_layout(**PL,height=270,barmode="stack",
        title=dict(text=f"{T['bloc4_chart_title']} · {ctx['scope_label']}",font=dict(color=th["text"],size=13)),
        legend=dict(font=dict(color=th["text2"],size=11),bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(**GRID); fig.update_yaxes(**GRID)
    st.plotly_chart(fig, width="stretch")
    sources_bar(f"{T['sources_cecc']} · {T['sources_barker']} · {T['sources_bauer']}", th)
