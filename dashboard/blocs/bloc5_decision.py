"""blocs/bloc5_decision.py — Décision santé (New PDF + Original Gauge UI Merge)"""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import io
import os
import joblib
from datetime import date, timedelta
from utils import get_context, banner, img_card, sources_bar, empty_state, irs_level, niveau_contextuel
from assets import IMAGES

_SNK_TO_KEY    = {"faible":"normal","modere":"watch","eleve":"high","critique":"urgent"}
_SNK_TO_STATUS = {"faible":"bloc5_status_normal","modere":"bloc5_status_watch",
                  "eleve":"bloc5_status_high","critique":"bloc5_status_urgent"}
_SNK_TO_MAYOR  = {"faible":"bloc5_status_calm","modere":"bloc5_status_watch",
                  "eleve":"bloc5_status_alert","critique":"bloc5_status_crisis"}

# ── Chargement seuils contextuels ────────────────────────────────────────────
@st.cache_resource
def _load_seuils_ctx():
    base = os.path.dirname(os.path.abspath(__file__))
    for c in [os.path.join(base, '..', 'models'), os.path.join(base, '..', '..', 'models')]:
        p = os.path.join(c, 'seuils_contextuels.pkl')
        if os.path.exists(p):
            return joblib.load(p)
    return None

def _get_p90_ville(ville):
    """Retourne le seuil p90 contextuel pour une ville."""
    sc = _load_seuils_ctx()
    if sc is None:
        return None
    return sc.get('par_ville', {}).get(ville, None)

# ── Carte KPI ville ───────────────────────────────────────────────────────────
def _kpi_card(irs, snt, snc, pm25, col_ctx_hex, niv_ctx, p90_ville, th, lang="fr", titre="Risque Sanitaire"):
    """Carte IRS + PM2.5 OMS — sans contexte camerounais."""
    pm25_col = th["green"] if pm25 <= 15 else th["red"]
    oms_label = "PM2.5 · WHO LIMIT" if lang == "en" else "PM2.5 · SEUIL OMS"
    st.markdown(
        f'<div style="background:{th["bg_elevated"]};border:4px solid {snc};'
        f'border-radius:15px;padding:20px 15px;text-align:center;height:200px;'
        f'box-sizing:border-box;'
        f'display:flex;flex-direction:column;justify-content:center;'
        f'box-shadow:0 10px 25px {snc}44;">'
        f'<div style="font-size:11px;color:{th["text"]};font-weight:950;'
        f'text-transform:uppercase;margin-bottom:6px;">{titre}</div>'
        f'<div style="font-size:46px;font-weight:950;color:{snc};line-height:0.9;">{irs:.3f}</div>'
        f'<div style="font-size:16px;font-weight:950;margin-top:8px;text-transform:uppercase;">{snt}</div>'
        f'<div style="margin-top:8px;padding-top:6px;border-top:1px solid {snc}33;">'
        f'<div style="font-size:9px;color:{th["text"]};font-weight:bold;text-transform:uppercase;'
        f'letter-spacing:.06em;">{oms_label}</div>'
        f'<div style="font-size:12px;font-weight:700;color:{pm25_col};">'
        f'{pm25:.1f} µg/m³ · {pm25/15:.1f}x</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

def _ctx_card(niv_ctx, col_ctx_hex, p90_ville, pm25, th, lang):
    """Carte contexte camerounais — niveau local basé sur p90 historique."""
    if not niv_ctx or not p90_ville:
        st.markdown(
            f'<div style="background:{th["bg_elevated"]};border:2px solid {th["border_soft"]};'
            f'border-radius:15px;padding:20px 15px;text-align:center;height:200px;'
            f'box-sizing:border-box;'
            f'display:flex;flex-direction:column;justify-content:center;">'
            f'<div style="font-size:11px;color:{th["text3"]};">{"Context unavailable" if lang=="en" else "Contexte non disponible"}</div>'
            f'</div>', unsafe_allow_html=True)
        return
    ratio     = pm25 / p90_ville
    ratio_col = th["green"] if ratio < 0.5 else th["amber"] if ratio < 0.75 else th["coral"] if ratio < 1.0 else th["red"]
    barre_w   = min(int(ratio * 100), 100)
    st.markdown(
        f'<div style="background:{th["bg_elevated"]};border:4px solid {col_ctx_hex};'
        f'border-radius:15px;padding:20px 15px;text-align:center;height:200px;'
        f'box-sizing:border-box;'
        f'display:flex;flex-direction:column;justify-content:center;'
        f'box-shadow:0 10px 25px {col_ctx_hex}44;">'
        f'<div style="font-size:11px;color:{th["text"]};font-weight:950;'
        f'text-transform:uppercase;margin-bottom:6px;">{"PM2.5 THRESHOLD · CAMEROON CONTEXT" if lang=="en" else "SEUIL PM2.5 · CONTEXTE CAMEROUN"}</div>'
        f'<div style="font-size:28px;font-weight:950;color:{col_ctx_hex};line-height:1;">{niv_ctx}</div>'
        f'<div style="font-size:10px;color:{th["text3"]};margin-top:6px;">'
        f'{"Local threshold p90=" if lang=="en" else "Seuil local p90 ="} {p90_ville:.1f} µg/m³</div>'
        f'<div style="margin-top:8px;">'
        f'<div style="background:{th["bg_tertiary"]};border-radius:4px;height:6px;overflow:hidden;">'
        f'<div style="background:{col_ctx_hex};height:100%;width:{barre_w}%;border-radius:4px;"></div>'
        f'</div>'
        f'<div style="font-size:10px;color:{col_ctx_hex};margin-top:4px;font-weight:700;">'
        f'{pm25:.1f} / {p90_ville:.1f} µg/m³ · {ratio*100:.0f}{"% of threshold" if lang=="en" else "% du seuil"}</div>'
        f'</div>'
        f'<div style="margin-top:6px;padding-top:6px;border-top:1px solid {col_ctx_hex}33;">'
        f'<div style="font-size:9px;color:{th["text3"]};">'
        f'Réf. · {"Historical 90th percentile 2022-2026" if lang=="en" else "Percentile 90 historique 2022-2026"} · INS Cameroun (2019)</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ── Génération PDF ────────────────────────────────────────────────────────────
def _generer_pdf(ville, date_rapport, pm25, irs, niveau, ratio_oms,
                 poll_dom, snk, preds, lang, niv_ctx=None, p90_ville=None):
    """Génère un rapport PDF beau, pro et complet sur une page A4."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas as pdfcanvas
        from datetime import date as ddate, timedelta

        W, H = A4
        buffer = __import__("io").BytesIO()
        c = pdfcanvas.Canvas(buffer, pagesize=A4)

        DARK   = colors.HexColor("#0f172a")
        DARK2  = colors.HexColor("#1e293b")
        TEAL   = colors.HexColor("#00d4b1")
        WHITE  = colors.white
        GRAY   = colors.HexColor("#64748b")
        LIGHT  = colors.HexColor("#f8fafc")
        LIGHT2 = colors.HexColor("#f1f5f9")
        SLATE  = colors.HexColor("#94a3b8")
        BORDER = colors.HexColor("#e2e8f0")

        niv_color = {
            "faible":   colors.HexColor("#10b981"),
            "modere":   colors.HexColor("#f59e0b"),
            "eleve":    colors.HexColor("#f97316"),
            "critique": colors.HexColor("#ef4444"),
        }.get(snk, GRAY)

        niv_bg = {
            "faible":   colors.HexColor("#ecfdf5"),
            "modere":   colors.HexColor("#fffbeb"),
            "eleve":    colors.HexColor("#fff7ed"),
            "critique": colors.HexColor("#fef2f2"),
        }.get(snk, LIGHT)

        niv_label = {"faible":"LOW","modere":"MODERATE","eleve":"HIGH","critique":"CRITICAL"}.get(snk, niveau) if lang=="en" else {"faible":"FAIBLE","modere":"MODERE","eleve":"ELEVE","critique":"CRITIQUE"}.get(snk, niveau)
        niv_desc  = {"faible":"Satisfactory air quality","modere":"Moderate quality - Caution",
                     "eleve":"High quality - Alert","critique":"CRITICAL HEALTH DANGER"}.get(snk, "") if lang=="en" else {"faible":"Air de qualite satisfaisante","modere":"Qualite moderee - Prudence",
                     "eleve":"Qualite elevee - Alerte","critique":"DANGER SANITAIRE CRITIQUE"}.get(snk, "")

        TN  = "Times-Roman"
        TNB = "Times-Bold"
        HV  = "Helvetica"
        HVB = "Helvetica-Bold"
        M   = 1.5*cm
        IW  = W - 2*M

        # ── HEADER ───────────────────────────────────────────────────────────
        HDR_H = 3.8*cm
        c.setFillColor(DARK)
        c.rect(0, H - HDR_H, W, HDR_H, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(0, H - 0.35*cm, W, 0.35*cm, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(0, H - HDR_H, 0.4*cm, HDR_H, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.setFont(TNB, 26)
        c.drawString(1.2*cm, H - 1.65*cm, "AirSentinel Cameroun")
        c.setFillColor(SLATE)
        c.setFont(TN, 9)
        c.drawString(1.2*cm, H - 2.25*cm, "Daily Health Report · DPA Green Tech · IndabaX Cameroon 2026" if lang=="en" else "Rapport Sanitaire Quotidien  ·  DPA Green Tech  ·  IndabaX Cameroon 2026")
        c.setStrokeColor(colors.HexColor("#1e3a5f"))
        c.setLineWidth(0.5)
        c.line(1.2*cm, H - 2.65*cm, W - M, H - 2.65*cm)
        c.setFillColor(colors.HexColor("#475569"))
        c.setFont(TN, 8)
        c.drawString(1.2*cm, H - 3.1*cm, "Environmental health surveillance report · Open-Meteo Data" if lang=="en" else "Rapport de surveillance environnementale et sanitaire · Donnees Open-Meteo")
        c.setFillColor(WHITE)
        c.setFont(TNB, 15)
        c.drawRightString(W - M, H - 1.65*cm, f"City : {ville}" if lang=="en" else f"Ville : {ville}")
        c.setFillColor(TEAL)
        c.setFont(TNB, 10)
        c.drawRightString(W - M, H - 2.25*cm, f"Date : {date_rapport}")

        # ── NIVEAU + KPIs + CONTEXTE CAMEROUN ───────────────────────────────
        S2T = H - HDR_H - 0.5*cm
        S2H = 3.5*cm

        # Fond global
        c.setFillColor(niv_bg)
        c.roundRect(M, S2T - S2H, IW, S2H, 10, fill=1, stroke=0)
        c.setStrokeColor(niv_color)
        c.setLineWidth(1.5)
        c.roundRect(M, S2T - S2H, IW, S2H, 10, fill=0, stroke=1)

        # Calcul couleur contexte
        ctx_col = GRAY
        ctx_bg  = colors.HexColor("#f8fafc")
        if niv_ctx and p90_ville:
            if "NORMAL" in niv_ctx:
                ctx_col = colors.HexColor("#10b981"); ctx_bg = colors.HexColor("#ecfdf5")
            elif "ÉLEVÉ" in niv_ctx:
                ctx_col = colors.HexColor("#f59e0b"); ctx_bg = colors.HexColor("#fffbeb")
            elif "PIC" in niv_ctx:
                ctx_col = colors.HexColor("#ef4444"); ctx_bg = colors.HexColor("#fef2f2")
            else:
                ctx_col = colors.HexColor("#f97316"); ctx_bg = colors.HexColor("#fff7ed")

        # Largeurs des 6 éléments : badge | pm25 | irs | oms | polluant | contexte
        BW  = 3.5*cm   # badge niveau
        KW  = (IW - BW - 0.4*cm) / 5   # 5 cases égales
        PAD = 0.4*cm   # espace entre badge et KPIs

        def _kpi_box(x, y, w, h, lbl, val, unit, bc, tc):
            """Dessine un KPI box."""
            c.setFillColor(WHITE)
            c.roundRect(x + 0.08*cm, y, w - 0.16*cm, h, 7, fill=1, stroke=0)
            c.setStrokeColor(BORDER)
            c.setLineWidth(0.4)
            c.roundRect(x + 0.08*cm, y, w - 0.16*cm, h, 7, fill=0, stroke=1)
            # Bande haut
            c.setFillColor(bc)
            c.roundRect(x + 0.08*cm, y + h - 0.4*cm, w - 0.16*cm, 0.4*cm, 7, fill=1, stroke=0)
            c.rect(x + 0.08*cm, y + h - 0.4*cm, w - 0.16*cm, 0.2*cm, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont(HVB, 6)
            c.drawCentredString(x + w/2, y + h - 0.25*cm, lbl)
            c.setFillColor(tc)
            c.setFont(TNB, 12)
            c.drawCentredString(x + w/2, y + 0.85*cm, val)
            c.setFillColor(GRAY)
            c.setFont(TN, 6.5)
            c.drawCentredString(x + w/2, y + 0.35*cm, unit)

        KY  = S2T - S2H + 0.3*cm
        KH  = S2H - 0.6*cm

        # Badge niveau
        c.setFillColor(niv_color)
        c.roundRect(M + 0.3*cm, KY, BW - 0.3*cm, KH, 10, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(TNB, 17)
        c.drawCentredString(M + BW/2, KY + KH - 1.0*cm, niv_label)
        c.setFont(TN, 6.5)
        c.drawCentredString(M + BW/2, KY + KH - 1.5*cm, niv_desc)

        # 4 KPIs
        kpis_data = [
            ("AVG PM2.5" if lang=="en" else "PM2.5 MOYEN",   f"{pm25:.1f}",      "µg/m³",     niv_color),
            ("IRS INDEX" if lang=="en" else "INDICE IRS",    f"{irs:.3f}",        "ACP·INS2019",niv_color),
            ("WHO LIMIT" if lang=="en" else "SEUIL OMS",     f"{ratio_oms:.1f}x", "exceeded" if lang=="en" else "depassement",niv_color),
            ("MAIN POLLUT." if lang=="en" else "POLLUANT DOM.", poll_dom[:8],         "dominant",  niv_color),
        ]
        for i, (lbl, val, unit, bc) in enumerate(kpis_data):
            _kpi_box(M + BW + PAD + i*KW, KY, KW, KH, lbl, val, unit, bc, bc)

        # Cadre contexte camerounais
        CTX_X = M + BW + PAD + 4*KW
        c.setFillColor(ctx_bg)
        c.roundRect(CTX_X + 0.08*cm, KY, KW - 0.16*cm, KH, 7, fill=1, stroke=0)
        c.setStrokeColor(ctx_col)
        c.setLineWidth(1.2)
        c.roundRect(CTX_X + 0.08*cm, KY, KW - 0.16*cm, KH, 7, fill=0, stroke=1)
        # Bande haut contexte
        c.setFillColor(ctx_col)
        c.roundRect(CTX_X + 0.08*cm, KY + KH - 0.4*cm, KW - 0.16*cm, 0.4*cm, 7, fill=1, stroke=0)
        c.rect(CTX_X + 0.08*cm, KY + KH - 0.4*cm, KW - 0.16*cm, 0.2*cm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(HVB, 6)
        c.drawCentredString(CTX_X + KW/2, KY + KH - 0.25*cm, "CMR CONTEXT" if lang=="en" else "CONTEXTE CMR")
        if niv_ctx and p90_ville:
            c.setFillColor(ctx_col)
            c.setFont(TNB, 11)
            c.drawCentredString(CTX_X + KW/2, KY + 0.85*cm, niv_ctx)
            c.setFillColor(GRAY)
            c.setFont(TN, 6)
            c.drawCentredString(CTX_X + KW/2, KY + 0.35*cm, f"p90={p90_ville:.1f} µg/m³")
        else:
            c.setFillColor(GRAY)
            c.setFont(TN, 7)
            c.drawCentredString(CTX_X + KW/2, KY + 0.6*cm, "N/A")

        # ── PRÉDICTIONS 72H ───────────────────────────────────────────────────
        S3T = S2T - S2H - 0.5*cm
        S3H = 4.2*cm
        c.setFillColor(DARK2)
        c.roundRect(M, S3T - S3H, IW, S3H, 10, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.setFont(TNB, 11)
        c.drawCentredString(W/2, S3T - 0.42*cm, "PM2.5 PREDICTIONS · 72 HOURS" if lang=="en" else "PREDICTIONS PM2.5  ·  72 HEURES")
        c.setFillColor(SLATE)
        c.setFont(TN, 7)
        c.drawCentredString(W/2, S3T - 0.75*cm, "Hybrid Model RL+ARIMA · MAE = 3.456 · R² = 0.893" if lang=="en" else "Modele Hybride RL+ARIMA  ·  MAE = 3.456  ·  R² = 0.893")
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setLineWidth(0.4)
        c.line(M + 0.5*cm, S3T - 0.95*cm, M + IW - 0.5*cm, S3T - 0.95*cm)

        jours_lbl = ["Today", "Tomorrow", "Day after tomorrow"] if lang=="en" else ["Aujourd'hui", "Demain", "Apres-demain"]
        jours_dt  = [ddate.today() + timedelta(days=i) for i in range(3)]
        CW = IW / 3
        for i, (lbl, dt, pred) in enumerate(zip(jours_lbl, jours_dt, preds)):
            pc  = (colors.HexColor("#10b981") if pred<=15 else colors.HexColor("#f59e0b")
                   if pred<=25 else colors.HexColor("#f97316") if pred<=37.5 else colors.HexColor("#ef4444"))
            pniv_oms = ("LOW" if pred<=15 else "MODERATE" if pred<=25 else "HIGH" if pred<=37.5 else "CRITICAL") if lang=="en" else ("FAIBLE" if pred<=15 else "MODERE" if pred<=25 else "ELEVE" if pred<=37.5 else "CRITIQUE")
            cx = M + i * CW + CW/2

            # Niveau contextuel pour cette prédiction
            if p90_ville and p90_ville > 0:
                ratio_p = pred / p90_ville
                if   ratio_p < 0.50: pniv_ctx = "NORMAL";     pc_ctx = colors.HexColor("#10b981")
                elif ratio_p < 0.75: pniv_ctx = "MODERE";      pc_ctx = colors.HexColor("#f59e0b")
                elif ratio_p < 1.0:  pniv_ctx = "ELEVE";       pc_ctx = colors.HexColor("#f97316")
                else:                pniv_ctx = "PIC ANORMAL";  pc_ctx = colors.HexColor("#ef4444")
            else:
                pniv_ctx = None; pc_ctx = GRAY

            if i > 0:
                c.setStrokeColor(colors.HexColor("#334155"))
                c.setLineWidth(0.4)
                c.line(M + i*CW, S3T - 1.85*cm, M + i*CW, S3T - S3H + 0.3*cm)

            # Jour + date
            c.setFillColor(WHITE)
            c.setFont(TNB, 10)
            c.drawCentredString(cx, S3T - 1.2*cm, lbl.encode("latin-1", "replace").decode("latin-1"))
            c.setFillColor(SLATE)
            c.setFont(TN, 7.5)
            c.drawCentredString(cx, S3T - 1.6*cm, dt.strftime("%d / %m / %Y"))

            # Valeur prédite
            c.setFillColor(pc)
            c.setFont(TNB, 15)
            c.drawCentredString(cx, S3T - 2.3*cm, f"{pred:.1f} µg/m³")

            # Niveau OMS
            c.setFillColor(pc)
            c.setFont(HVB, 8)
            c.drawCentredString(cx, S3T - 2.8*cm, f"WHO: {pniv_oms}" if lang=="en" else f"OMS : {pniv_oms}")

            # Niveau contextuel
            if pniv_ctx:
                c.setFillColor(pc_ctx)
                c.setFont(HVB, 8)
                c.drawCentredString(cx, S3T - 3.3*cm, f"CMR : {pniv_ctx}")

        # ── RECOMMANDATIONS ───────────────────────────────────────────────────
        S4T = S3T - S3H - 0.5*cm
        S4H = 4.5*cm
        c.setFillColor(TEAL)
        c.rect(M, S4T - 0.32*cm, 0.22*cm, 0.32*cm, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.setFont(TNB, 10)
        c.drawString(M + 0.4*cm, S4T - 0.26*cm, "RECOMMENDATIONS BY PROFILE" if lang=="en" else "RECOMMANDATIONS PAR PROFIL")
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.line(M, S4T - 0.48*cm, M + IW, S4T - 0.48*cm)

        profils = [
            ("Citizen" if lang=="en" else "Citoyen",   _get_reco_text(snk, "citizen", lang)),
            ("Doctor" if lang=="en" else "Medecin",    _get_reco_text(snk, "health", lang)),
            ("Mayor" if lang=="en" else "Maire",       _get_reco_text(snk, "mayor", lang)),
            ("Researcher" if lang=="en" else "Chercheur", _get_reco_text(snk, "researcher", lang)),
        ]
        RH = (S4H - 0.6*cm) / 4
        for i, (plbl, preco) in enumerate(profils):
            ry = S4T - 0.6*cm - i * RH
            if i % 2 == 0:
                c.setFillColor(LIGHT2)
                c.rect(M, ry - RH, IW, RH, fill=1, stroke=0)
            BPW = 2.6*cm
            c.setFillColor(niv_color)
            c.roundRect(M + 0.2*cm, ry - RH + 0.15*cm, BPW, RH - 0.3*cm, 6, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont(TNB, 9)
            c.drawCentredString(M + 0.2*cm + BPW/2, ry - RH/2 - 0.05*cm, plbl)
            c.setFillColor(DARK)
            c.setFont(TN, 8.5)
            short = preco[:100] + ("..." if len(preco) > 100 else "")
            c.drawString(M + BPW + 0.5*cm, ry - RH/2 - 0.05*cm, short)

        # ── POPULATIONS VULNÉRABLES ───────────────────────────────────────────
        S5T = S4T - S4H - 0.5*cm
        S5H = 4.0*cm
        c.setFillColor(TEAL)
        c.rect(M, S5T - 0.32*cm, 0.22*cm, 0.32*cm, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.setFont(TNB, 10)
        c.drawString(M + 0.4*cm, S5T - 0.26*cm, "VULNERABLE POPULATIONS" if lang=="en" else "POPULATIONS VULNERABLES")
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.5)
        c.line(M, S5T - 0.48*cm, M + IW, S5T - 0.48*cm)

        vuln = VULN_EN[snk] if lang == "en" else VULN_FR[snk]
        pops = [("Children" if lang=="en" else "Enfants",vuln["enfants"]),("Pregnant" if lang=="en" else "Enceintes",vuln["enceintes"]),
                ("Seniors" if lang=="en" else "Ages",vuln["ages"]),("Asthma",vuln["asthma"]),("Agricult.",vuln["agricult"])]
        VCW = IW / 5
        VCH = S5H - 0.65*cm
        for i, (plbl, preco) in enumerate(pops):
            vx = M + i * VCW
            vy = S5T - 0.6*cm
            c.setFillColor(WHITE)
            c.roundRect(vx + 0.18*cm, vy - VCH, VCW - 0.36*cm, VCH, 8, fill=1, stroke=0)
            c.setStrokeColor(niv_color)
            c.setLineWidth(0.8)
            c.roundRect(vx + 0.18*cm, vy - VCH, VCW - 0.36*cm, VCH, 8, fill=0, stroke=1)
            c.setFillColor(niv_color)
            c.roundRect(vx + 0.18*cm, vy - 0.65*cm, VCW - 0.36*cm, 0.65*cm, 8, fill=1, stroke=0)
            c.rect(vx + 0.18*cm, vy - 0.65*cm, VCW - 0.36*cm, 0.3*cm, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont(TNB, 8.5)
            c.drawCentredString(vx + VCW/2, vy - 0.44*cm, plbl)
            txt = preco.replace("✅","").replace("⚠️","").replace("🚨","").replace("🔴","").strip()
            words = txt.split()
            lines, cur = [], []
            for w in words:
                if len(" ".join(cur + [w])) <= 22: cur.append(w)
                else: lines.append(" ".join(cur)); cur = [w]
            if cur: lines.append(" ".join(cur))
            lines = lines[:5]
            c.setFillColor(DARK)
            c.setFont(TN, 7)
            total_h = len(lines) * 0.38*cm
            start_y = vy - 0.65*cm - (VCH - 0.65*cm)/2 + total_h/2 - 0.1*cm
            for li, ln in enumerate(lines):
                c.drawCentredString(vx + VCW/2, start_y - li * 0.38*cm, ln)

        # ── FOOTER ────────────────────────────────────────────────────────────
        FH = 1.4*cm
        c.setFillColor(DARK)
        c.rect(0, 0, W, FH, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(0, FH, W, 0.15*cm, fill=1, stroke=0)
        c.setFillColor(SLATE)
        c.setFont(TN, 6.5)
        c.drawString(M, 0.55*cm,
            "Sources : WHO AQG 2021  ·  NCBI NBK574591  ·  Chen & Hoek (2020)  ·  INS Cameroun (2019)  ·  Open-Meteo API")
        c.setFillColor(TEAL)
        c.setFont(TNB, 7)
        c.drawRightString(W - M, 0.55*cm,
            f"AirSentinel  ·  DPA Green Tech  ·  IndabaX 2026  ·  {date_rapport}")

        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        return None


def _get_reco_text(snk, profil_key, lang="fr"):
    reco_map_fr = {
        "faible":   {"citizen":"Qualité de l'air satisfaisante. Activités normales autorisées.",
                     "health":"Pas d'alerte sanitaire. Surveillance de routine suffisante.",
                     "mayor":"Situation normale. Aucune mesure d'urgence requise.",
                     "researcher":"Données conformes aux seuils OMS. Niveau de base."},
        "modere":   {"citizen":"Réduire les activités intenses en extérieur. Porter un masque en cas de gêne.",
                     "health":"Surveiller les patients sensibles. Anticiper une légère hausse des consultations.",
                     "mayor":"Diffuser des recommandations préventives. Surveiller l'évolution.",
                     "researcher":"Dépassement IT4 (25 µg/m³). Analyser les sources d'émission locales."},
        "eleve":    {"citizen":"Limiter les sorties. Fermer les fenêtres. Éviter l'effort physique.",
                     "health":"Alerter les patients asthmatiques. Renforcer les stocks d'inhalateurs.",
                     "mayor":"Déclencher une alerte publique. Réduire les sources de pollution locales.",
                     "researcher":"Dépassement IT3 (37.5 µg/m³). Identifier l'épisode climatique en cours."},
        "critique": {"citizen":"DANGER — Rester confiné. Ne pas sortir. Consulter un médecin si symptômes.",
                     "health":"URGENCE SANITAIRE — Activer le protocole d'urgence respiratoire.",
                     "mayor":"CRISE — Déclencher le plan d'urgence sanitaire. Alertes SMS obligatoires.",
                     "researcher":"Dépassement critique (>75 µg/m³). Documenter l'épisode et les causes."},
    }
    reco_map_en = {
        "faible":   {"citizen":"Satisfactory air quality. Normal activities allowed.",
                     "health":"No health alert. Routine surveillance is sufficient.",
                     "mayor":"Normal situation. No emergency measures required.",
                     "researcher":"Data complies with WHO limits. Baseline level."},
        "modere":   {"citizen":"Reduce intense outdoor activities. Wear a mask if symptoms occur.",
                     "health":"Monitor sensitive patients. Anticipate a slight increase in consultations.",
                     "mayor":"Broadcast preventive recommendations. Monitor the situation.",
                     "researcher":"IT4 exceeded (25 µg/m³). Analyze local emission sources."},
        "eleve":    {"citizen":"Limit outings. Close windows. Avoid physical effort.",
                     "health":"Alert asthmatic patients. Reinforce inhaler stocks.",
                     "mayor":"Trigger public alert. Reduce local pollution sources.",
                     "researcher":"IT3 exceeded (37.5 µg/m³). Identify the current weather episode."},
        "critique": {"citizen":"DANGER — Stay confined. Do not go out. Consult a doctor if symptoms.",
                     "health":"HEALTH EMERGENCY — Activate respiratory emergency protocol.",
                     "mayor":"CRISIS — Trigger health emergency plan. Mandatory SMS alerts.",
                     "researcher":"Critical exceedance (>75 µg/m³). Document the episode and causes."},
    }
    reco_map = reco_map_en if lang == "en" else reco_map_fr
    return reco_map.get(snk, {}).get(profil_key, "—")

VULN_FR = {
    "faible":   {"enfants":"Excellente qualité d'air. Privilégiez les jeux et sports en plein air.",
                 "enceintes":"Profitez de l'extérieur sans restriction. Aérez bien votre intérieur.",
                 "ages":"Moment idéal pour vos promenades et activités physiques régulières.",
                 "asthma":"Risque très faible. Poursuivez vos traitements de fond normalement.",
                 "agricult":"Conditions de travail optimales. Aucune restriction respiratoire."},
    "modere":   {"enfants":"Les enfants sensibles doivent éviter les efforts sportifs intenses.",
                 "enceintes":"Limitez le temps passé à proximité des grands axes routiers.",
                 "ages":"Réduisez les efforts cardio-vasculaires prolongés en extérieur.",
                 "asthma":"Surveillez l'apparition de toux. Ayez vos secours sur vous.",
                 "agricult":"Restez vigilants face aux poussières. Masque conseillé si épandage."},
    "eleve":    {"enfants":"Évitez strictement les sports extérieurs. Limitez les récréations.",
                 "enceintes":"Sorties brèves uniquement. Éloignez-vous des zones à fort trafic.",
                 "ages":"Évitez toute sortie non essentielle. Gardez les fenêtres fermées.",
                 "asthma":"Prenez votre traitement préventif. Ne sortez qu'en cas d'urgence.",
                 "agricult":"Décalez les travaux pénibles tôt le matin. Port d'un masque FFP2 requis."},
    "critique": {"enfants":"DANGER — Confinement total à l'intérieur. Aucune activité physique.",
                 "enceintes":"DANGER — Restez à domicile. Consultez au moindre doute respiratoire.",
                 "ages":"DANGER — Confinement strict. N'aérez que très tard la nuit.",
                 "asthma":"DANGER CRITIQUE — Risque de crise. Médicament d'urgence à portée, appelez le 15.",
                 "agricult":"DANGER — Arrêt impératif des travaux manuels extérieurs. Cabine filtrée uniquement."},
}
VULN_EN = {
    "faible":   {"enfants":"Excellent air quality. Favour outdoor play and sports.",
                 "enceintes":"Enjoy outdoors without restriction. Ventilate your home well.",
                 "ages":"Perfect time for walks and regular physical outdoor activities.",
                 "asthma":"Very low risk. Continue your basic treatments normally.",
                 "agricult":"Optimal field working conditions. No respiratory restrictions."},
    "modere":   {"enfants":"Sensitive children should limit intense outdoor sports.",
                 "enceintes":"Limit prolonged time spent along heavy traffic roads.",
                 "ages":"Reduce prolonged cardiovascular efforts outdoors.",
                 "asthma":"Watch for signs of cough. Keep rescue inhaler at hand.",
                 "agricult":"Stay vigilant with dust. Mask recommended if spraying."},
    "eleve":    {"enfants":"Strictly avoid outdoor sports. Limit playground activities.",
                 "enceintes":"Brief outings only. Avoid high traffic and congested areas.",
                 "ages":"Avoid non-essential outings. Keep windows closed during peaks.",
                 "asthma":"Take preventive medication. Go out only in emergencies.",
                 "agricult":"Shift hard work to early morning. FFP2 mask is required."},
    "critique": {"enfants":"DANGER — Strict indoor confinement. No physical activity at all.",
                 "enceintes":"DANGER — Stay home. Consult a doctor at any respiratory doubt.",
                 "ages":"DANGER — Strict confinement. Ventilate only very late at night.",
                 "asthma":"DANGER CRITIQUE — High crisis risk. Emergency meds nearby, call 911/15.",
                 "agricult":"DANGER — Stop all outdoor manual work. Filtered cabin machinery only."},
}

def _vuln_section(snk, lang, th):
    data = VULN_FR[snk] if lang == "fr" else VULN_EN[snk]
    color_map = {"faible":th["green"],"modere":th["amber"],"eleve":th["coral"],"critique":th["red"]}
    cc = color_map[snk]
    
    # Icône de statut SVG (petite pour les cartes)
    icon_check = f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
    icon_warn  = f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    icon_siren = f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M7 18v-6a5 5 0 1 1 10 0v6"/><path d="M5 21h14"/><path d="M12 7v5"/><path d="M12 17v2"/></svg>'
    icon_crit  = f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
    
    icon_status = {"faible":icon_check,"modere":icon_warn,"eleve":icon_siren,"critique":icon_crit}[snk]

    svg_child  = f'<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>'
    svg_women  = f'<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="5"/><path d="M12 13v9"/><path d="M9 18h6"/></svg>'
    svg_senior = f'<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="15" r="4"/><circle cx="18" cy="15" r="4"/><path d="M14 15a2 2 0 0 0-4 0"/><path d="M2.5 13L5 7c.7-1.3 1.4-2 3-2"/><path d="M21.5 13L19 7c-.7-1.3-1.5-2-3-2"/></svg>'
    svg_asthma = f'<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v9"/><path d="M8 11c-2.5-3-5.5-2.5-5.5 1.5 0 5 3.5 9.5 9.5 9.5V11"/><path d="M16 11c2.5-3 5.5-2.5 5.5 1.5 0 5-3.5 9.5-9.5 9.5V11"/></svg>'
    svg_agri   = f'<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{cc}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>'
    pops = [(svg_child,"CHILDREN" if lang=="en" else "ENFANTS","enfants"),(svg_women,"WOMEN" if lang=="en" else "FEMMES","enceintes"),
            (svg_senior,"SENIORS" if lang=="en" else "SÉNIORS","ages"),(svg_asthma,"ASTHMA" if lang=="en" else "ASTHME","asthma"),(svg_agri,"AGRICULT." if lang=="en" else "AGRICUL.","agricult")]
    nom_fr = {"faible":"NIVEAU FAIBLE (VERT)","modere":"NIVEAU MODÉRÉ (JAUNE)","eleve":"NIVEAU ÉLEVÉ (ORANGE)","critique":"NIVEAU CRITIQUE (ROUGE)"}
    nom_en = {"faible":"LOW LEVEL (GREEN)","modere":"MODERATE LEVEL (YELLOW)","eleve":"HIGH LEVEL (ORANGE)","critique":"CRITICAL LEVEL (RED)"}
    niveau_lbl = nom_fr[snk] if lang == "fr" else nom_en[snk]
    st.markdown(
        f'<div style="margin-top:15px;padding:15px;background:{th["bg_tertiary"]};'
        f'border:2px solid {cc}88;border-top:5px solid {cc};border-radius:15px;">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
        f'<div style="font-size:14px;font-weight:950;color:{th["text"]};text-transform:uppercase;letter-spacing:.15em;">' + ("ACTION BOARD · VULNERABLE POPULATIONS" if lang=="en" else "TABLEAU D'ACTION · POPULATIONS VULNÉRABLES") + '</div>'
        f'<div style="background:{cc}22;color:{cc};padding:4px 10px;border-radius:6px;font-weight:900;font-size:12px;">{niveau_lbl}</div>'
        f'</div>', unsafe_allow_html=True)
    cols = st.columns(len(pops))
    for col, (icon, label, key) in zip(cols, pops):
        with col:
            st.markdown(
                f'<div style="background:{th["bg_elevated"]};border:1px solid {th["border_soft"]};'
                f'border-radius:12px;padding:12px 10px;height:145px;text-align:center;">'
                f'<div style="font-size:28px;margin-bottom:6px;">{icon}</div>'
                f'<div style="font-size:12px;font-weight:950;color:{cc};margin-bottom:8px;letter-spacing:1px;">{label}</div>'
                f'<div style="font-size:12px;color:{th["text"]};line-height:1.4;text-align:left;font-weight:800;display:flex;align-items:flex-start;gap:6px;">'
                f'<span style="margin-top:2px; flex-shrink:0;">{icon_status}</span>'
                f'<span>{data[key]}</span></div>'
                f'</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def _rec_content(profil, profil_map, snk, tkey, snc, snt, ctx, th, T, scope_label, lang="fr"):
    pk = profil_map.get(profil, "citizen")
    icon_mayor = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right:8px; vertical-align:text-bottom;"><path d="M7 18v-6a5 5 0 1 1 10 0v6"/><path d="M5 21h14"/><path d="M12 7v5"/><path d="M12 17v2"/></svg>'
    if pk == "health":
        primary_action = T.get(f"bloc5_med_{tkey}", "Stable status." if lang=="en" else "Statut stable.")
    elif pk == "mayor":
        acts = T.get(f"bloc5_mayor_{tkey}", ["Veille administrative active."])
        primary_action = f"{icon_mayor} {acts[0]}" if len(acts) > 0 else ("Active watch." if lang=="en" else "Veille active.")
    else:
        primary_action = T.get(f"bloc4_msg_{snk}_{pk}", T.get(f"bloc4_msg_{snk}_citizen", "\u2014"))
    if len(primary_action) > 120:
        primary_action = primary_action[:117] + "..."
    st.markdown(
        f'<div style="background:{th["bg_tertiary"]};border:1px solid {th["border_soft"]};'
        f'border-radius:12px;padding:20px 18px;height:200px;box-sizing:border-box;'
        f'display:flex;flex-direction:column;justify-content:center;">'
        f'<div style="font-size:20px;font-weight:950;color:{snc};margin-bottom:10px;'
        f'text-transform:uppercase;letter-spacing:1px;">{T[_SNK_TO_STATUS[snk]]}</div>'
        f'<div style="font-size:15px;color:{th["text"]};font-weight:800;line-height:1.5;">{primary_action}</div>'
        f'</div>', unsafe_allow_html=True)

def _render_exceptional_radial_gauge(irs, ctx, th):
    p50, p75, p90 = ctx["p50"], ctx["p75"], ctx["p90"]
    fig = go.Figure(go.Indicator(
        mode="gauge", value=irs, domain={'x':[0,1],'y':[0,1]},
        gauge={
            'axis':{'range':[0,1],'tickwidth':2,'tickcolor':th['text'],
                    'tickvals':[0,p50,p75,p90,1],
                    'ticktext':["<b>0</b>",f"<b>{p50:.2f}</b>",f"<b>{p75:.2f}</b>",f"<b>{p90:.2f}</b>","<b>1</b>"],
                    'tickfont':{"size":11,"family":"Arial Black, sans-serif","color":th['text']},
                    'ticks': ""},
            'bar':{'color':th['text'],'thickness':0.12},
            'bgcolor':"rgba(0,0,0,0.05)",
            'steps':[{'range':[0,p50],'color':th["green"]},{'range':[p50,p75],'color':th["amber"]},
                     {'range':[p75,p90],'color':th["coral"]},{'range':[p90,1.0],'color':th["red"]}],
            'threshold':{'line':{'color':"#fff",'width':3},'thickness':0.75,'value':irs}
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={'color':th['text2'],'family':"Arial, sans-serif"}, height=200,
        margin=dict(l=28,r=28,t=12,b=0),
        annotations=[dict(text=f"<b>{irs:.3f}</b>",x=0.5,y=0.08,xref="paper",yref="paper",
                          xanchor="center",yanchor="bottom",showarrow=False,
                          font=dict(size=28,color=th['text'],family="Arial, sans-serif"))]
    )
    return fig

def render(profil):
    ctx  = get_context()
    df   = ctx["df_brut"]
    th   = ctx["th"]
    T    = ctx["T"]
    lang = ctx["lang"]
    if len(df) == 0: empty_state(T, th); return

    profil_map = {T["sidebar_profile_citizen"]:"citizen", T["sidebar_profile_health"]:"health",
                  T["sidebar_profile_mayor"]:"mayor", T["sidebar_profile_researcher"]:"researcher"}

    dec_title   = "DÉCISION SANITAIRE" if lang == "fr" else "HEALTH DECISION"
    choisir_lbl = ":material/location_on: " + ("**FILTRER VILLE**" if lang == "fr" else "**FILTER CITY**")

    villes_dispo = sorted(df["ville"].unique().tolist())
    hcol1, hcol2, hcol3 = st.columns([2.2, 0.8, 1.3])

    with hcol2:
        st.markdown('<div style="height:5px;"></div>', unsafe_allow_html=True)
        ville_dec = st.selectbox(choisir_lbl, villes_dispo, key="v5_city_top_header")

    an_min, an_max_sel = st.session_state.get("annee_sel",
        (int(df["date"].dt.year.min()), int(df["date"].dt.year.max())))
    df_ville = df[(df["ville"] == ville_dec) &
                  (df["date"].dt.year >= an_min) &
                  (df["date"].dt.year <= an_max_sel)]
    scope_label = f"{ville_dec.upper()} · {an_min}–{an_max_sel}"

    if len(df_ville) == 0: empty_state(T, th); return

    pm25_ville   = float(df_ville["pm2_5_moyen"].mean())
    irs_ville    = float(df_ville["IRS"].mean())
    poll_dom_val = (df_ville["polluant_dominant"].value_counts().index[0]
                    if "polluant_dominant" in df_ville.columns else "PM2.5")
    snc, snt, snk = irs_level(irs_ville, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
    tkey = _SNK_TO_KEY[snk]

    # ── Niveau contextuel camerounais ─────────────────────────────────────────
    niv_ctx, col_ctx = niveau_contextuel(pm25_ville, ville_dec)
    if lang == "en" and niv_ctx:
        niv_ctx = niv_ctx.replace("MODÉRÉ", "MODERATE").replace("ÉLEVÉ", "HIGH").replace("PIC ANORMAL", "ABNORMAL PEAK")
    col_ctx_hex = {"green":th["green"],"amber":th["amber"],
                   "coral":th["coral"],"red":th["red"]}.get(col_ctx, th["text3"])
    p90_ville = _get_p90_ville(ville_dec)

    # ── Prédictions PDF ───────────────────────────────────────────────────────
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        chemins  = [os.path.join(base_dir,'..','models'), os.path.join(base_dir,'..','..','models')]
        _mod = _sca = _fea = _ari = None
        for c in chemins:
            if os.path.exists(os.path.join(c, 'meilleur_modele.pkl')):
                _mod = joblib.load(os.path.join(c, 'meilleur_modele.pkl'))
                _sca = joblib.load(os.path.join(c, 'scaler.pkl'))
                _fea = joblib.load(os.path.join(c, 'features.pkl'))
                _ari = joblib.load(os.path.join(c, 'arima_par_zone.pkl'))
                break
        ZONES_R = {'Zone équatoriale':['Centre','Est','Sud','Littoral','Sud-Ouest','Ouest','Nord-Ouest'],
                   'Zone soudanienne':['Adamaoua','Nord'],'Zone soudano-sahélienne':['Extreme-Nord']}
        def _zone(reg):
            for z, rs in ZONES_R.items():
                if reg in rs: return z
            return 'Zone équatoriale'
        df_v2   = df[df['ville'] == ville_dec].sort_values('date')
        region2 = df_v2['region'].iloc[-1] if len(df_v2) > 0 else 'Centre'
        zone2   = _zone(region2)
        preds_pdf = []
        if _mod and _sca and _fea and _ari:
            for step in range(1, 4):
                try:
                    last  = df_v2[_fea].fillna(df_v2[_fea].median()).tail(1)
                    p_rl  = _mod.predict(_sca.transform(last))[0]
                    p_ar  = _ari[zone2].forecast(steps=step).iloc[-1]
                    preds_pdf.append(max(0, p_rl + p_ar))
                except: preds_pdf.append(pm25_ville)
        else: preds_pdf = [pm25_ville] * 3
    except: preds_pdf = [pm25_ville] * 3

    # ── En-tête ───────────────────────────────────────────────────────────────
    with hcol1:
        banner(IMAGES["sante_banner"], 120, dec_title, profil.upper(), th, no_frame=False)

    with hcol3:
        st.markdown("""<style>
            div.stDownloadButton > button {
                font-weight:900 !important; color:#fff !important;
                background-color:#2563eb !important; border:none !important;
                border-radius:8px !important; padding:8px 10px !important;
                font-size:10px !important; width:100% !important;
            }
            div.stDownloadButton > button:hover { background-color:#1d4ed8 !important; }
        </style>""", unsafe_allow_html=True)
        st.markdown('<div style="height:15px;"></div>', unsafe_allow_html=True)
        c_p, c_c = st.columns(2, gap="small")
        with c_p:
            date_rapport = str(df["date"].max().date())
            niveau_txt   = {"faible":"LOW","modere":"MODERATE","eleve":"HIGH","critique":"CRITICAL"}[snk] if lang=="en" else {"faible":"FAIBLE","modere":"MODÉRÉ","eleve":"ÉLEVÉ","critique":"CRITIQUE"}[snk]
            pdf_bytes = _generer_pdf(
                ville=ville_dec, date_rapport=date_rapport, pm25=pm25_ville,
                irs=irs_ville, niveau=niveau_txt, ratio_oms=pm25_ville/15,
                poll_dom=poll_dom_val, snk=snk, preds=preds_pdf, lang=lang,
                niv_ctx=niv_ctx, p90_ville=p90_ville
            )
            if pdf_bytes:
                st.download_button(label=":material/description: DOWNLOAD PDF" if lang=="en" else ":material/description: TÉLÉCHARGER PDF", data=pdf_bytes,
                    file_name=f"airsentinel_{ville_dec}_{date_rapport}.pdf",
                    mime="application/pdf", key="v5_btn_pdf_top")
        with c_c:
            cols_csv = ['date','ville','region','pm2_5_moyen','pm2_5_max','IRS',
                        'niveau_sanitaire','polluant_dominant','temperature_2m_max',
                        'wind_speed_10m_max','precipitation_sum','dust_moyen','us_aqi_moyen']
            csv_data = (df_ville[[c for c in cols_csv if c in df_ville.columns]].copy())
            st.download_button(label=":material/download: DOWNLOAD CSV" if lang=="en" else ":material/download: TÉLÉCHARGER CSV",
                data=csv_data.to_csv(index=False).encode('utf-8'),
                file_name=f"airsentinel_{ville_dec}_{date_rapport}.csv",
                mime="text/csv", key="v5_btn_csv_top")

    # ── Onglets ───────────────────────────────────────────────────────────────
    sub1, sub2 = st.tabs(["**REAL DATA**", "**IRS SIMULATOR**"] if lang == "en" else ["**DONNÉES RÉELLES**", "**SIMULATEUR IRS**"])

    with sub1:
        m_col1, m_col2, m_col3, m_col4 = st.columns([0.9, 1.3, 1.0, 1.3])
        with m_col1:
            _kpi_card(irs_ville, snt, snc, pm25_ville,
                      col_ctx_hex, niv_ctx, p90_ville, th, lang=lang,
                      titre="Health Risk" if lang=="en" else "Risque Sanitaire")
        with m_col2:
            st.plotly_chart(_render_exceptional_radial_gauge(irs_ville, ctx, th),
                width='stretch', config={'displayModeBar':False,'responsive':True},
                key="gauge_v5_real_trio")
        with m_col3:
            _ctx_card(niv_ctx, col_ctx_hex, p90_ville, pm25_ville, th, lang)
        with m_col4:
            _rec_content(profil, profil_map, snk, tkey, snc, snt, ctx, th, T, scope_label, lang)
        _vuln_section(snk, lang, th)

    with sub2:
        irs_v = st.slider("SIMULATED MODIFICATION:" if lang=="en" else "MODIFICATION SIMULÉE :", 0.0, 1.0,
                          float(irs_ville), 0.001, key="v5_sim_final_trio")
        snc_s, snt_s, snk_s = irs_level(irs_v, ctx["p50"], ctx["p75"], ctx["p90"], T, th)
        tkey_s = _SNK_TO_KEY[snk_s]

        # Niveau contextuel simulé basé sur IRS simulé → recalculer pm25 approx
        pm25_sim = irs_v * 80  # approximation linéaire pour le simulateur
        niv_ctx_s, col_ctx_s = niveau_contextuel(pm25_sim, ville_dec)
        if lang == "en" and niv_ctx_s:
            niv_ctx_s = niv_ctx_s.replace("MODÉRÉ", "MODERATE").replace("ÉLEVÉ", "HIGH").replace("PIC ANORMAL", "ABNORMAL PEAK")
        col_ctx_hex_s = {"green":th["green"],"amber":th["amber"],
                         "coral":th["coral"],"red":th["red"]}.get(col_ctx_s, th["text3"])

        m_col1_s, m_col2_s, m_col3_s, m_col4_s = st.columns([0.9, 1.3, 1.0, 1.3])
        with m_col1_s:
            _kpi_card(irs_v, snt_s, snc_s, pm25_sim,
                      col_ctx_hex_s, niv_ctx_s, p90_ville, th, lang=lang,
                      titre="Simulated Risk" if lang=="en" else "Risque Simulé")
        with m_col2_s:
            st.plotly_chart(_render_exceptional_radial_gauge(irs_v, ctx, th),
                width='stretch', config={'displayModeBar':False,'responsive':True},
                key="gauge_v5_sim_trio")
        with m_col3_s:
            _ctx_card(niv_ctx_s, col_ctx_hex_s, p90_ville, pm25_sim, th, lang)
        with m_col4_s:
            _rec_content(profil, profil_map, snk_s, tkey_s, snc_s, snt_s, ctx, th, T, scope_label, lang)
        _vuln_section(snk_s, lang, th)

    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    sources_bar(f":material/analytics: DECISIONAL ANALYSIS · INDABAX 2026" if lang=="en" else f":material/analytics: ANALYSE DÉCISIONNELLE · INDABAX 2026", th)