"""blocs/bloc6_shap.py — Profil climatique dynamique par zone — Objectif OS3
Zones INS Cameroun (2019) · Visualisations interactives · Impact sanitaire
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import get_context, sources_bar, empty_state

# ── Zones INS Cameroun (2019) ─────────────────────────────────────────────────
ZONES_META = {
    'Zone équatoriale': {
        'regions': ['Centre', 'Est', 'Sud', 'Littoral', 'Sud-Ouest', 'Ouest', 'Nord-Ouest'],
        'color':   '#10b981',
        'emoji':   '🌿',
        'desc':    'Forêt équatoriale · Feux de brousse · 2 saisons des pluies',
        'facteur': 'Feux de brousse en saison sèche (jan-fév)',
        'ref':     'Gordon et al. (2023) · Barker et al. (2020)',
    },
    'Zone soudanienne': {
        'regions': ['Adamaoua', 'Nord'],
        'color':   '#f59e0b',
        'emoji':   '🌾',
        'desc':    'Savane soudanienne · 5-6 mois saison sèche · Transition',
        'facteur': 'Dust sahélien + inversions thermiques nocturnes',
        'ref':     'INS Cameroun (2019) · Annuaire Statistique',
    },
    'Zone soudano-sahélienne': {
        'regions': ['Extreme-Nord'],
        'color':   '#ef4444',
        'emoji':   '🏜️',
        'desc':    'Steppe sahélienne · 7-9 mois saison sèche · Harmattan',
        'facteur': 'Poussière saharienne (dust dominant)',
        'ref':     'Schepanski et al. (2007) · Knippertz et al. (2008)',
    },
}

RECO = {
    'Zone équatoriale': {
        'citoyen': [
            '😷 Jan-fév : portez un masque lors des sorties extérieures',
            '🪟 Fermez les fenêtres pendant les épisodes de feux de brousse',
            '🏃 Évitez le sport en extérieur de décembre à mars',
            '🌿 Plantez des arbres — la végétation filtre les particules fines',
        ],
        'medecin': [
            '🏥 Anticipez +40% de consultations respiratoires en jan-fév',
            '💊 Renforcez les stocks d\'inhalateurs dès décembre',
            '👶 Surveillance accrue des enfants et personnes âgées en saison sèche',
            '📋 Informez vos patients asthmatiques dès novembre',
        ],
        'maire': [
            '📢 Déclenchez des alertes publiques dès janvier (PM2.5 > 3x OMS)',
            '🚧 Interdisez les feux agricoles en saison sèche (jan-mar)',
            '🏫 Réduisez les activités extérieures scolaires en jan-fév',
            '🌳 Investissez dans des espaces verts urbains',
        ],
        'chercheur': [   # ← ajouter ici
            '📊 Analyser la corrélation entre épisodes de feux et pics PM2.5 en jan-fév',
            '🔬 Étudier l\'impact de l\'harmattan sur la composition chimique des particules',
            '📡 Déployer des capteurs low-cost pour densifier le réseau de mesure',
            '📝 Publier les données AirSentinel en open data pour la communauté scientifique',
        ],

    },

    'Zone soudanienne': {
        'citoyen': [
            '😷 Portez un masque en jan-fév — PM2.5 dépasse 2.8x le seuil OMS',
            '🌙 Évitez les sorties matinales — les nuits froides piègent les polluants',
            '🔥 Limitez la combustion domestique en saison sèche',
            '💧 Hydratez-vous — l\'air sec aggrave les irritations respiratoires',
        ],
        'medecin': [
            '🏥 Pic de consultations en jan-fév — PM2.5 dépasse 2.8x le seuil OMS',
            '🌡️ Surveillez les pathologies liées aux inversions thermiques',
            '💊 Anticipez les crises d\'asthme et BPCO dès décembre',
            '📊 Tenez un registre des cas respiratoires pour détecter les pics',
        ],
        'maire': [
            '📢 Alertes publiques recommandées de décembre à mars',
            '🚗 Réduisez la circulation en centre-ville aux heures matinales',
            '🏗️ Suspendez les chantiers poussièreux en jan-fév',
            '📡 Installez des capteurs de qualité de l\'air',
        ],
        'chercheur': [   # ← ajouter ici
        '📊 Modéliser l\'impact des inversions thermiques nocturnes sur PM2.5',
        '🌡️ Étudier la relation dust sahélien — maladies respiratoires dans l\'Adamaoua',
        '🔬 Analyser la composition minérale des poussières transportées par l\'harmattan',
        '📝 Comparer les profils saisonniers avec les données de mortalité régionales',
        ],
    },
    'Zone soudano-sahélienne': {
        'citoyen': [
            '😷 Port du masque obligatoire en jan-fév — PM2.5 dépasse 3.6x le seuil OMS',
            '🏠 Restez à l\'intérieur lors des tempêtes de sable',
            '👁️ Protégez yeux et voies respiratoires — dust très élevé',
            '💧 Humidifiez l\'air intérieur — l\'air sec aggrave l\'impact',
        ],
        'medecin': [
            '🚨 ALERTE — PM2.5 dépasse 3.6x le seuil OMS en février',
            '🏥 Renforcez les urgences respiratoires de décembre à mars',
            '👶 Surveillance maximale des nourrissons et personnes âgées',
            '📋 Protocole méningite — l\'harmattan favorise sa propagation',
        ],
        'maire': [
            '🚨 Déclenchez le plan d\'urgence sanitaire dès janvier',
            '📢 Alertes quotidiennes obligatoires via radio et SMS en jan-fév',
            '🏫 Fermez les écoles lors des pics de dust extrêmes',
            '🛣️ Arrosez les routes non goudronnées pour limiter la poussière',
        ],
        'chercheur': [   # ← ajouter ici
            '📊 Quantifier la contribution du dust saharien vs sources locales au PM2.5',
            '🏥 Corréler les pics de PM2.5 avec les admissions hospitalières à Maroua',
            '🌍 Étudier le lien harmattan — épidémies de méningite dans l\'Extrême-Nord',
            '📡 Proposer un réseau de surveillance transfrontalier avec le Tchad et le Niger',
        ],
    },
}

MOIS = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']

# Couleurs de fond opaques selon le thème
BG_CARD  = "rgba(15,23,42,0.97)"       # fond carte opaque dark
BG_CARD2 = "rgba(20,30,50,0.97)"       # fond carte légèrement différent
BG_HEAD  = "rgba(10,18,35,0.98)"       # fond header très opaque


def _rgb(hex_color):
    h = hex_color.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


@st.cache_data(ttl=3600)
def _calc_zones_stats(_df_hash, df):
    zones_stats = {}
    for nom_zone, meta in ZONES_META.items():
        df_z = df[df['region'].isin(meta['regions'])]
        if len(df_z) == 0:
            continue
        pm25_mois = {}
        for m in range(1, 13):
            val = df_z[df_z['date'].dt.month == m]['pm2_5_moyen'].mean()
            pm25_mois[m] = round(float(val), 2) if not np.isnan(val) else 0.0
        zones_stats[nom_zone] = {
            **meta,
            'pm25':      float(df_z['pm2_5_moyen'].mean()),
            'dust':      float(df_z['dust_moyen'].mean()) if 'dust_moyen' in df_z.columns else 0,
            'temp':      float(df_z['temperature_2m_max'].mean()) if 'temperature_2m_max' in df_z.columns else 30,
            'precip':    float(df_z['precipitation_sum'].mean()) if 'precipitation_sum' in df_z.columns else 0,
            'harmattan': float(df_z['harmattan_intense'].mean() * 100) if 'harmattan_intense' in df_z.columns else 0,
            'feux':      float(df_z['episode_feux'].mean() * 100) if 'episode_feux' in df_z.columns else 0,
            'pm25_mois': pm25_mois,
        }
    return zones_stats


def render(profil):
    ctx  = get_context()
    th   = ctx['th']
    T    = ctx['T']
    df   = ctx['df_brut']
    lang = ctx['lang']

    if len(df) == 0:
        empty_state(T, th)
        return

    ZONES = _calc_zones_stats(len(df), df)
    if not ZONES:
        empty_state(T, th)
        return

    GRID = dict(gridcolor=th['grid_color'], linecolor=th['line_color'], zeroline=False)
    PL   = dict(paper_bgcolor='rgba(15,23,42,0.97)', plot_bgcolor='rgba(20,30,50,0.95)',
                font=dict(color=th['text2'], size=11))

    annees = f"{df['date'].dt.year.min()}–{df['date'].dt.year.max()}"

    # Adapter les fonds selon le thème
    is_dark = th.get('name', 'dark') == 'dark'
    bg_card  = "rgba(15,23,42,0.97)"  if is_dark else "rgba(255,255,255,0.97)"
    bg_card2 = "rgba(20,30,50,0.97)"  if is_dark else "rgba(245,248,255,0.97)"
    bg_head  = "rgba(10,18,35,0.98)"  if is_dark else "rgba(230,240,255,0.98)"
    txt_main = th['text']
    txt_sub  = th['text2']
    txt_dim  = th['text3']
    border   = th['border_soft']

    # ══════════════════════════════════════════════════════════════════════════
    # EN-TÊTE
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="background:{bg_head};'
        f'border:1px solid {th["teal"]}44;border-left:4px solid {th["teal"]};'
        f'border-radius:12px;padding:16px 20px;margin-bottom:20px;">'
        f'<div style="font-size:10px;letter-spacing:.14em;text-transform:uppercase;'
        f'color:{th["teal"]};font-family:DM Mono,monospace;margin-bottom:6px;">'
        f'Objectif OS3 · IndabaX 2026 · INS Cameroun (2019)</div>'
        f'<div style="font-size:16px;font-weight:600;color:{txt_main};margin-bottom:4px;">'
        f'Profil climatique & facteurs aggravants par zone</div>'
        f'<div style="font-size:12px;color:{txt_sub};">'
        f'3 zones climatiques · Données {annees} · WHO AQG 2021 · NCBI NBK574591'
        f'</div></div>',
        unsafe_allow_html=True
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SÉLECTEUR DE ZONE
    # ══════════════════════════════════════════════════════════════════════════
    zone_sel = st.radio(
        label='Zone',
        options=list(ZONES.keys()),
        format_func=lambda z: f"{ZONES[z]['emoji']} {z}",
        horizontal=True,
        label_visibility='collapsed',
        key='zone_selector_bloc6'
    )
    meta_sel = ZONES[zone_sel]
    rv, gv, bv = _rgb(meta_sel['color'])

    # Info zone — fond opaque
    st.markdown(
        f'<div style="background:{bg_card};'
        f'border:1px solid {meta_sel["color"]}66;'
        f'border-left:4px solid {meta_sel["color"]};'
        f'border-radius:10px;padding:14px 18px;margin:10px 0 20px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<div>'
        f'<div style="font-size:15px;font-weight:600;color:{meta_sel["color"]};">'
        f'{meta_sel["emoji"]} {zone_sel}</div>'
        f'<div style="font-size:11px;color:{txt_sub};margin-top:4px;">{meta_sel["desc"]}</div>'
        f'<div style="font-size:11px;color:{txt_main};margin-top:6px;">'
        f'⚡ Facteur dominant : <strong style="color:{meta_sel["color"]};">{meta_sel["facteur"]}</strong>'
        f'</div></div>'
        f'<div style="text-align:right;font-size:10px;color:{txt_dim};'
        f'font-family:DM Mono,monospace;line-height:1.8;">'
        f'{"<br>".join(meta_sel["regions"])}</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    # ══════════════════════════════════════════════════════════════════════════
    # KPIs — fond opaque
    # ══════════════════════════════════════════════════════════════════════════
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpis = [
        (k1, f"{meta_sel['pm25']:.1f}", 'PM2.5 moy.', 'µg/m³',
         th['red'] if meta_sel['pm25'] > 25 else th['amber'] if meta_sel['pm25'] > 15 else th['green']),
        (k2, f"{meta_sel['dust']:.0f}", 'Dust moy.', 'µg/m³',
         th['red'] if meta_sel['dust'] > 50 else th['amber'] if meta_sel['dust'] > 20 else th['green']),
        (k3, f"{meta_sel['temp']:.1f}°", 'Temp. max', 'moy.',
         th['coral'] if meta_sel['temp'] > 32 else th['amber']),
        (k4, f"{meta_sel['precip']:.1f}", 'Précip.', 'mm/jour',
         th['blue'] if meta_sel['precip'] > 4 else th['amber']),
        (k5, f"{meta_sel['harmattan']:.1f}%", 'Harmattan', 'fréq.',
         th['red'] if meta_sel['harmattan'] > 5 else th['green']),
        (k6, f"{meta_sel['feux']:.1f}%", 'Feux', 'fréq.',
         th['red'] if meta_sel['feux'] > 2 else th['green']),
    ]
    for col_ui, val, label, unit, color in kpis:
        with col_ui:
            st.markdown(
                f'<div style="background:{bg_card};'
                f'border:1px solid {color}66;'
                f'border-top:4px solid {color};'
                f'border-radius:12px;padding:16px 8px;text-align:center;'
                f'box-shadow:0 4px 20px {color}22;">'
                f'<div style="font-size:28px;font-weight:800;color:{color};'
                f'line-height:1;letter-spacing:-0.5px;'
                f'text-shadow:0 0 20px {color}66;">{val}</div>'
                f'<div style="font-size:10px;color:{txt_main};margin-top:6px;'
                f'font-weight:600;text-transform:uppercase;letter-spacing:.06em;">{label}</div>'
                f'<div style="font-size:9px;color:{txt_dim};margin-top:2px;">{unit}</div>'
                f'</div>',
                unsafe_allow_html=True
        )

    st.markdown("<div style='margin:20px 0 8px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — INSIGHT + QUE FAIRE côte à côte
    # ══════════════════════════════════════════════════════════════════════════
    pm25_mois = meta_sel['pm25_mois']
    pic_mois  = max(pm25_mois, key=pm25_mois.get)
    pic_val   = pm25_mois[pic_mois]
    bas_mois  = min(pm25_mois, key=pm25_mois.get)
    bas_val   = pm25_mois[bas_mois]
    amplitude = pic_val - bas_val

    col_ins, col_rec = st.columns([1, 1])

    with col_ins:
        st.markdown(
            f'<div style="background:{bg_card};'
            f'border:1px solid {meta_sel["color"]}55;'
            f'border-radius:12px;padding:16px 20px;min-height:380px;overflow-y:auto;">'
            f'<div style="font-size:13px;font-weight:600;color:{meta_sel["color"]};margin-bottom:14px;">'
            f'{meta_sel["emoji"]} Insight — {zone_sel}</div>'

            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;'
            f'padding:10px;background:rgba({rv},{gv},{bv},0.12);border-radius:8px;">'
            f'<div style="font-size:24px;">📈</div>'
            f'<div>'
            f'<div style="font-size:10px;color:{txt_dim};text-transform:uppercase;letter-spacing:.06em;">Pic saisonnier</div>'
            f'<div style="font-size:16px;font-weight:700;color:{th["red"]};">{MOIS[pic_mois-1]} · {pic_val:.1f} µg/m³</div>'
            f'<div style="font-size:10px;color:{txt_sub};">{(pic_val/15):.1f}x le seuil OMS</div>'
            f'</div></div>'

            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;'
            f'padding:10px;background:rgba(16,185,129,0.12);border-radius:8px;">'
            f'<div style="font-size:24px;">📉</div>'
            f'<div>'
            f'<div style="font-size:10px;color:{txt_dim};text-transform:uppercase;letter-spacing:.06em;">Minimum saisonnier</div>'
            f'<div style="font-size:16px;font-weight:700;color:{th["green"]};">{MOIS[bas_mois-1]} · {bas_val:.1f} µg/m³</div>'
            f'<div style="font-size:10px;color:{txt_sub};">{"Conforme OMS" if bas_val <= 15 else "Dépasse OMS"}</div>'
            f'</div></div>'

            f'<div style="display:flex;align-items:center;gap:12px;'
            f'padding:10px;background:rgba({rv},{gv},{bv},0.10);border-radius:8px;">'
            f'<div style="font-size:24px;">⚡</div>'
            f'<div>'
            f'<div style="font-size:10px;color:{txt_dim};text-transform:uppercase;letter-spacing:.06em;">Amplitude saisonnière</div>'
            f'<div style="font-size:16px;font-weight:700;color:{meta_sel["color"]};">{amplitude:.1f} µg/m³</div>'
            f'<div style="font-size:10px;color:{txt_sub};">{meta_sel["facteur"]}</div>'
            f'</div></div>'

            f'<div style="font-size:9px;color:{txt_dim};margin-top:12px;font-family:DM Mono,monospace;">'
            f'📚 {meta_sel["ref"]} · INS Cameroun (2019)</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col_rec:
        profil_key = 'citoyen'
        if profil and hasattr(profil, 'lower'):
            p = profil.lower()
            if 'med' in p or 'sant' in p:
                profil_key = 'medecin'
            elif 'mai' in p or 'auto' in p or 'polit' in p or 'dec' in p:
                profil_key = 'maire'
            elif 'cherch' in p or 'research' in p:
                profil_key = 'chercheur'

        profil_labels = {
            'citoyen': '👤 Citoyen',
            'medecin': '🩺 Médecin / Soignant',
            'maire':   '🏛️ Maire / Décideur',
            'chercheur': '🔬 Chercheur / Scientifique',
        }

        recos = RECO.get(zone_sel, {}).get(profil_key, [])
        reco_html = ''.join([
            f'<div style="display:flex;align-items:flex-start;gap:10px;'
            f'padding:10px 12px;margin-bottom:8px;'
            f'background:rgba({rv},{gv},{bv},0.12);'
            f'border:1px solid {meta_sel["color"]}33;'
            f'border-radius:8px;">'
            f'<div style="font-size:18px;flex-shrink:0;">{r[:2]}</div>'
            f'<div style="font-size:11px;color:{txt_sub};line-height:1.5;">{r[2:].strip()}</div>'
            f'</div>'
            for r in recos
        ])

        st.markdown(
            f'<div style="background:{bg_card};'
            f'border:1px solid {meta_sel["color"]}55;'
            f'border-radius:12px;padding:16px 20px;min-height:380px;overflow-y:auto;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
            f'<div style="font-size:13px;font-weight:600;color:{meta_sel["color"]};">'
            f'{meta_sel["emoji"]} Que faire ?</div>'
            f'<div style="font-size:10px;color:{txt_dim};font-family:DM Mono,monospace;'
            f'background:rgba({rv},{gv},{bv},0.20);padding:3px 10px;border-radius:20px;">'
            f'{profil_labels[profil_key]}</div>'
            f'</div>'
            f'{reco_html}'
            f'<div style="font-size:9px;color:{txt_dim};margin-top:10px;font-family:DM Mono,monospace;">'
            f'Basées sur · WHO AQG 2021 · INS Cameroun (2019) · {annees}'
            f'</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin:20px 0 8px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — COMPARAISON DÉTAILLÉE DES INDICATEURS
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:{txt_main};margin-bottom:12px;">'
        f'📊 Comparaison détaillée des indicateurs — 3 zones</div>',
        unsafe_allow_html=True
    )

    indicateurs = {
        'PM2.5 (µg/m³)':  'pm25',
        'Dust (µg/m³)':   'dust',
        'Temp. max (°C)': 'temp',
        'Précip. (mm/j)': 'precip',
    }

    fig_bars = go.Figure()
    for nom_zone, meta in ZONES.items():
        rv2, gv2, bv2 = _rgb(meta['color'])
        is_sel = nom_zone == zone_sel
        fig_bars.add_trace(go.Bar(
            name=f"{meta['emoji']} {nom_zone.replace('Zone ','')}",
            x=list(indicateurs.keys()),
            y=[meta[k] for k in indicateurs.values()],
            marker=dict(
                color=f'rgba({rv2},{gv2},{bv2},{0.90 if is_sel else 0.45})',
                line=dict(width=2 if is_sel else 0,
                          color=meta['color'] if is_sel else f'rgba({rv2},{gv2},{bv2},0)')
            ),
            text=[f'{meta[k]:.1f}' for k in indicateurs.values()],
            textposition='outside',
            textfont=dict(size=11 if is_sel else 9,
                          color=meta['color'] if is_sel else f'rgba({rv2},{gv2},{bv2},0.7)'),
            hovertemplate=f"<b>{nom_zone}</b><br>%{{x}} : %{{y:.1f}}<extra></extra>",
        ))

    # Ligne seuil OMS PM2.5
    fig_bars.add_shape(
        type='line', x0=-0.5, x1=0.5, y0=15, y1=15,
        line=dict(color=th['red'], width=1.5, dash='dash'),
    )
    fig_bars.add_annotation(
        x=0, y=15, text="OMS 15", showarrow=False,
        font=dict(color=th['red'], size=9), yshift=8
    )

    fig_bars.update_layout(
        **PL, height=300, barmode='group',
        margin=dict(l=20, r=20, t=50, b=20),
        uniformtext_minsize=9, uniformtext_mode='hide',
        legend=dict(font=dict(color=txt_sub, size=10),
            bgcolor='rgba(15,23,42,0.95)',
            orientation='h',
            yanchor='top', y=1.15,
            xanchor='left', x=0),
        xaxis=dict(**GRID, tickfont=dict(size=11, color=txt_main)),
        yaxis=dict(**GRID, tickfont=dict(size=10, color=txt_main)),
    )
    st.plotly_chart(fig_bars, width="stretch")

    st.markdown("<div style='margin:20px 0 8px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — IMPACT SANITAIRE · Chen & Hoek (2020)
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:{txt_main};margin-bottom:12px;">'
        f'🏥 Impact sanitaire estimé · Chen & Hoek (2020) via WHO AQG 2021</div>',
        unsafe_allow_html=True
    )

    pm25_national = float(df['pm2_5_moyen'].mean())
    dep_national  = max(0, pm25_national - 15.0)
    red_national  = (dep_national / 10) * 6

    col_i1, col_i2, col_i3, col_i4 = st.columns([1, 1, 1, 2])
    zones_list = list(ZONES.items())

    for col_ui, (nom_zone, meta) in zip([col_i1, col_i2, col_i3], zones_list):
        pm25_z = meta['pm25']
        dep_z  = max(0, pm25_z - 15.0)
        red_z  = (dep_z / 10) * 6
        rv2, gv2, bv2 = _rgb(meta['color'])
        is_sel = nom_zone == zone_sel
        brd    = f'2px solid {meta["color"]}' if is_sel else f'1px solid {meta["color"]}44'
        with col_ui:
            st.markdown(
                f'<div style="background:{bg_card};'
                f'border:{brd};border-radius:12px;padding:14px;text-align:center;">'
                f'<div style="font-size:11px;color:{txt_dim};margin-bottom:6px;">'
                f'{meta["emoji"]} {nom_zone.replace("Zone ","")}</div>'
                f'<div style="font-size:24px;font-weight:700;color:{meta["color"]};">{pm25_z:.1f}</div>'
                f'<div style="font-size:10px;color:{txt_dim};">µg/m³</div>'
                f'<div style="font-size:11px;color:{txt_sub};margin-top:8px;'
                f'padding-top:8px;border-top:1px solid {meta["color"]}33;">'
                f'+{dep_z:.1f} µg/m³ vs OMS</div>'
                f'<div style="font-size:15px;font-weight:700;color:{th["red"]};margin-top:4px;">'
                f'→ -{red_z:.1f}%</div>'
                f'<div style="font-size:9px;color:{txt_dim};">mortalité cardiopulm.</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    with col_i4:
        st.markdown(
            f'<div style="background:{bg_head};'
            f'border:1px solid {th["teal"]}55;'
            f'border-left:4px solid {th["teal"]};'
            f'border-radius:12px;padding:16px 18px;">'
            f'<div style="font-size:12px;font-weight:600;color:{th["teal"]};margin-bottom:10px;">'
            f'🌍 Impact national — Cameroun</div>'
            f'<div style="font-size:13px;color:{txt_sub};line-height:1.8;">'
            f'PM2.5 moyen : <strong style="color:{th["amber"]};">{pm25_national:.1f} µg/m³</strong><br>'
            f'Dépassement OMS : <strong style="color:{txt_main};">+{dep_national:.1f} µg/m³</strong><br>'
            f'Si PM2.5 → 15 µg/m³ :<br>'
            f'<strong style="font-size:22px;color:{th["green"]};">-{red_national:.1f}%</strong>'
            f'<span style="font-size:11px;color:{txt_sub};"> mortalité cardiopulm.</span>'
            f'</div>'
            f'<div style="font-size:9px;color:{txt_dim};margin-top:10px;font-family:DM Mono,monospace;">'
            f'+10 µg/m³ PM2.5 → +6% mortalité cardiopulmonaire<br>'
            f'Chen & Hoek (2020) · NCBI NBK574591</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Sources ───────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    sources_bar(
        'INS Cameroun (2019) · WHO AQG 2021 · IPCC AR5 (2014) · '
        'Chen & Hoek (2020) · Schepanski et al. (2007) · Knippertz et al. (2008) · '
        'Gordon et al. (2023) PMC9884662 · Barker et al. (2020)',
        th
    )