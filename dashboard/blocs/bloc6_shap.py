"""blocs/bloc6_shap.py — Profil climatique dynamique par zone — Objectif OS3
Zones INS Cameroun (2019) · Visualisations interactives · Impact sanitaire
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import get_context, banner, sources_bar, empty_state
from assets import IMAGES

# ── Icônes SVG inline (pas de JS requis) ─────────────────────────────────────
ICONS_SVG = {
    "shield":        '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "trending-up":   '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "trending-down": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
    "zap":           '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "wind":          '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/></svg>',
    "flame":         '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
    "leaf":          '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>',
    "wheat":         '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 22 16 8"/><path d="M3.47 12.53 5 11l1.53 1.53a3.5 3.5 0 0 1 0 4.94L5 19l-1.53-1.53a3.5 3.5 0 0 1 0-4.94z"/><path d="M7.47 8.53 9 7l1.53 1.53a3.5 3.5 0 0 1 0 4.94L9 15l-1.53-1.53a3.5 3.5 0 0 1 0-4.94z"/><path d="M11.47 4.53 13 3l1.53 1.53a3.5 3.5 0 0 1 0 4.94L13 11l-1.53-1.53a3.5 3.5 0 0 1 0-4.94z"/><path d="M20 2h2v2a4 4 0 0 1-4 4h-2V6a4 4 0 0 1 4-4z"/><path d="M11.47 17.47 13 19l-1.53 1.53a3.5 3.5 0 0 1-4.94 0L5 19l1.53-1.53a3.5 3.5 0 0 1 4.94 0z"/></svg>',
    "sun":           '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>',
    "thermometer":   '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>',
    "droplets":      '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z"/><path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97"/></svg>',
    "bar-chart-2":   '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
    "microscope":    '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18h8"/><path d="M3 22h18"/><path d="M14 22a7 7 0 1 0 0-14h-1"/><path d="M9 14h2"/><path d="M9 12a2 2 0 0 1-2-2V6h6v4a2 2 0 0 1-2 2z"/><path d="M12 6V3a1 1 0 0 0-1-1H9a1 1 0 0 0-1 1v3"/></svg>',
    "megaphone":     '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/></svg>',
    "hospital":      '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6v4"/><path d="M14 14h-4"/><path d="M14 18h-4"/><path d="M14 8h-4"/><path d="M18 12h2a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2h2"/><path d="M18 22V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v18"/></svg>',
    "user":          '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "stethoscope":   '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/></svg>',
    "landmark":      '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>',
    "alert-triangle":'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    "pill":          '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7z"/><line x1="8.5" y1="8.5" x2="15.5" y2="15.5"/></svg>',
    "baby":          '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12h.01"/><path d="M15 12h.01"/><path d="M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/><path d="M19 6.3a9 9 0 0 1 1.8 3.9 2 2 0 0 1 0 3.6 9 9 0 0 1-17.6 0 2 2 0 0 1 0-3.6A9 9 0 0 1 12 3c2 0 3.5 1.1 3.5 2.5s-.9 2.5-2 2.5c-.8 0-1.5-.4-1.5-1"/></svg>',
    "clipboard-list":'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><line x1="12" y1="11" x2="16" y2="11"/><line x1="12" y1="16" x2="16" y2="16"/><line x1="8" y1="11" x2="8.01" y2="11"/><line x1="8" y1="16" x2="8.01" y2="16"/></svg>',
    "file-text":     '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    "radio":         '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/><path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/><circle cx="12" cy="12" r="2"/><path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"/><path d="M19.1 4.9C23 8.8 23 15.1 19.1 19"/></svg>',
    "moon":          '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    "ban":           '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>',
    "home":          '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "eye":           '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
    "car":           '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 17H3a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v9a2 2 0 0 1-2 2h-2"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>',
    "hard-hat":      '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 18a1 1 0 0 0 1 1h18a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v2z"/><path d="M10 10V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v5"/><path d="M4 15v-3a6 6 0 0 1 6-6h0"/><path d="M14 6h0a6 6 0 0 1 6 6v3"/></svg>',
    "globe":         '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "pie-chart":     '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    "activity":      '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "trees":         '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 10v.2A3 3 0 0 1 8.9 16v0H5v0h0a3 3 0 0 1-1-5.8V10a3 3 0 0 1 6 0z"/><path d="M7 16v6"/><path d="M13 19v3"/><path d="M12 19h8.3a1 1 0 0 0 .7-1.7L18 14h.3a1 1 0 0 0 .7-1.7L16 9h.2a1 1 0 0 0 .8-1.7L13 3l-1.4 1.5"/></svg>',
    "school":        '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m4 6 8-4 8 4"/><path d="m18 10 4 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-8l4-2"/><path d="M14 22v-4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v4"/><path d="M18 5v17"/><path d="M6 5v17"/><circle cx="12" cy="9" r="2"/></svg>',
    "tree-pine":     '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 14 3 3.3a1 1 0 0 1-.7 1.7H4.7a1 1 0 0 1-.7-1.7L7 14h-.3a1 1 0 0 1-.7-1.7L9 9h-.2A1 1 0 0 1 8 7.3L12 3l4 4.3a1 1 0 0 1-.8 1.7H15l3 3.3a1 1 0 0 1-.7 1.7H17z"/><path d="M12 22v-3"/></svg>',
    "map-pin":       '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "construction":  '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="8" rx="1"/><path d="M17 14v7"/><path d="M7 14v7"/><path d="M17 3v3"/><path d="M7 3v3"/><path d="M10 14 2.3 6.3"/><path d="m14 6 7.7 7.7"/><path d="m8 6 8 8"/></svg>',
    "cloud":         '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/></svg>',
    "siren":         '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 18v-6a5 5 0 1 1 10 0v6"/><path d="M5 21a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-1a1 1 0 0 0-1-1H6a1 1 0 0 0-1 1v1z"/><path d="M21 12h1"/><path d="M18.5 4.5 18 5"/><path d="M2 12h1"/><path d="M12 2v1"/><path d="M4.929 4.929 5.5 5.5"/></svg>',
}

def _icon(name, size=16, color="currentColor"):
    """Retourne le SVG inline de l'icône."""
    svg = ICONS_SVG.get(name, ICONS_SVG["map-pin"])
    return svg.format(s=size, c=color)

# ── Zones INS Cameroun (2019) ─────────────────────────────────────────────────
ZONES_META = {
    'Zone équatoriale': {
        'regions': ['Centre', 'Est', 'Sud', 'Littoral', 'Sud-Ouest', 'Ouest', 'Nord-Ouest'],
        'color':   '#10b981',
        'icon':    'leaf',
        'desc':    'Forêt équatoriale · Feux de brousse · 2 saisons des pluies',
        'facteur': 'Feux de brousse en saison sèche (jan-fév)',
        'ref':     'Gordon et al. (2023) · Barker et al. (2020)',
    },
    'Zone soudanienne': {
        'regions': ['Adamaoua', 'Nord'],
        'color':   '#f59e0b',
        'icon':    'wheat',
        'desc':    'Savane soudanienne · 5-6 mois saison sèche · Transition',
        'facteur': 'Dust sahélien + inversions thermiques nocturnes',
        'ref':     'INS Cameroun (2019) · Annuaire Statistique',
    },
    'Zone soudano-sahélienne': {
        'regions': ['Extreme-Nord'],
        'color':   '#ef4444',
        'icon':    'sun',
        'desc':    'Steppe sahélienne · 7-9 mois saison sèche · Harmattan',
        'facteur': 'Poussière saharienne (dust dominant)',
        'ref':     'Schepanski et al. (2007) · Knippertz et al. (2008)',
    },
}

RECO = {
    'Zone équatoriale': {
        'citoyen': [
            ('shield',         'Jan-fév : portez un masque lors des sorties extérieures'),
            ('wind',           'Fermez les fenêtres pendant les épisodes de feux de brousse'),
            ('activity',       'Évitez le sport en extérieur de décembre à mars'),
            ('tree-pine',      'Plantez des arbres — la végétation filtre les particules fines'),
        ],
        'medecin': [
            ('hospital',       'Anticipez +40% de consultations respiratoires en jan-fév'),
            ('pill',           'Renforcez les stocks d\'inhalateurs dès décembre'),
            ('baby',           'Surveillance accrue des enfants et personnes âgées en saison sèche'),
            ('clipboard-list', 'Informez vos patients asthmatiques dès novembre'),
        ],
        'maire': [
            ('megaphone',      'Déclenchez des alertes publiques dès janvier (PM2.5 > 3x OMS)'),
            ('ban',            'Interdisez les feux agricoles en saison sèche (jan-mar)'),
            ('school',         'Réduisez les activités extérieures scolaires en jan-fév'),
            ('trees',          'Investissez dans des espaces verts urbains'),
        ],
        'chercheur': [
            ('bar-chart-2',    'Analyser la corrélation entre épisodes de feux et pics PM2.5 en jan-fév'),
            ('microscope',     'Étudier l\'impact de l\'harmattan sur la composition chimique des particules'),
            ('radio',          'Déployer des capteurs low-cost pour densifier le réseau de mesure'),
            ('file-text',      'Publier les données AirSentinel en open data pour la communauté scientifique'),
        ],
    },
    'Zone soudanienne': {
        'citoyen': [
            ('shield',         'Portez un masque en jan-fév — PM2.5 dépasse 2.8x le seuil OMS'),
            ('moon',           'Évitez les sorties matinales — les nuits froides piègent les polluants'),
            ('flame',          'Limitez la combustion domestique en saison sèche'),
            ('droplets',       'Hydratez-vous — l\'air sec aggrave les irritations respiratoires'),
        ],
        'medecin': [
            ('hospital',       'Pic de consultations en jan-fév — PM2.5 dépasse 2.8x le seuil OMS'),
            ('thermometer',    'Surveillez les pathologies liées aux inversions thermiques'),
            ('pill',           'Anticipez les crises d\'asthme et BPCO dès décembre'),
            ('clipboard-list', 'Tenez un registre des cas respiratoires pour détecter les pics'),
        ],
        'maire': [
            ('megaphone',      'Alertes publiques recommandées de décembre à mars'),
            ('car',            'Réduisez la circulation en centre-ville aux heures matinales'),
            ('hard-hat',       'Suspendez les chantiers poussièreux en jan-fév'),
            ('radio',          'Installez des capteurs de qualité de l\'air'),
        ],
        'chercheur': [
            ('bar-chart-2',    'Modéliser l\'impact des inversions thermiques nocturnes sur PM2.5'),
            ('thermometer',    'Étudier la relation dust sahélien — maladies respiratoires dans l\'Adamaoua'),
            ('microscope',     'Analyser la composition minérale des poussières transportées par l\'harmattan'),
            ('file-text',      'Comparer les profils saisonniers avec les données de mortalité régionales'),
        ],
    },
    'Zone soudano-sahélienne': {
        'citoyen': [
            ('shield',         'Port du masque obligatoire en jan-fév — PM2.5 dépasse 3.6x le seuil OMS'),
            ('home',           'Restez à l\'intérieur lors des tempêtes de sable'),
            ('eye',            'Protégez yeux et voies respiratoires — dust très élevé'),
            ('droplets',       'Humidifiez l\'air intérieur — l\'air sec aggrave l\'impact'),
        ],
        'medecin': [
            ('alert-triangle', 'ALERTE — PM2.5 dépasse 3.6x le seuil OMS en février'),
            ('hospital',       'Renforcez les urgences respiratoires de décembre à mars'),
            ('baby',           'Surveillance maximale des nourrissons et personnes âgées'),
            ('clipboard-list', 'Protocole méningite — l\'harmattan favorise sa propagation'),
        ],
        'maire': [
            ('siren',          'Déclenchez le plan d\'urgence sanitaire dès janvier'),
            ('megaphone',      'Alertes quotidiennes obligatoires via radio et SMS en jan-fév'),
            ('school',         'Fermez les écoles lors des pics de dust extrêmes'),
            ('construction',   'Arrosez les routes non goudronnées pour limiter la poussière'),
        ],
        'chercheur': [
            ('pie-chart',      'Quantifier la contribution du dust saharien vs sources locales au PM2.5'),
            ('hospital',       'Corréler les pics de PM2.5 avec les admissions hospitalières à Maroua'),
            ('globe',          'Étudier le lien harmattan — épidémies de méningite dans l\'Extrême-Nord'),
            ('radio',          'Proposer un réseau de surveillance transfrontalier avec le Tchad et le Niger'),
        ],
    },
}

MOIS = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']


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
            'icon':      meta.get('icon', 'map-pin'),
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

    ZONES = _calc_zones_stats(str(len(df)) + '_v3', df)
    if not ZONES:
        empty_state(T, th)
        return

    GRID = dict(gridcolor=th['grid_color'], linecolor=th['line_color'], zeroline=False)
    PL   = dict(paper_bgcolor='rgba(15,23,42,0.97)', plot_bgcolor='rgba(20,30,50,0.95)',
                font=dict(color=th['text2'], size=11))

    annees  = f"{df['date'].dt.year.min()}–{df['date'].dt.year.max()}"
    is_dark = th.get('name', 'dark') == 'dark'
    bg_card = "rgba(15,23,42,0.97)" if is_dark else "rgba(255,255,255,0.97)"
    txt_main = th['text']
    txt_sub  = th['text2']
    txt_dim  = th['text3']

    # ══════════════════════════════════════════════════════════════════════════
    # EN-TÊTE + SÉLECTEUR DE ZONE côte à côte
    # ══════════════════════════════════════════════════════════════════════════
    col_banner6, col_zones6 = st.columns([2, 1])
    with col_banner6:
        banner(
            IMAGES["shap_banner"] if "shap_banner" in IMAGES else IMAGES["kpi_banner"],
            120, "PROFIL CLIMATIQUE", "", th, no_frame=False
        )
    with col_zones6:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        zone_sel = st.radio(
            label='Zone climatique',
            options=list(ZONES.keys()),
            format_func=lambda z: z,
            horizontal=False,
            key='zone_selector_bloc6'
        )

    meta_sel = ZONES[zone_sel]
    rv, gv, bv = _rgb(meta_sel['color'])

    # Info zone
    st.markdown(
        f'<div style="background:{bg_card};'
        f'border:1px solid {meta_sel["color"]}66;'
        f'border-left:4px solid {meta_sel["color"]};'
        f'border-radius:10px;padding:14px 18px;margin:10px 0 20px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<div>'
        f'<div style="font-size:17px;font-weight:700;color:{meta_sel["color"]};'
        f'display:flex;align-items:center;gap:8px;">'
        f'{_icon(meta_sel["icon"], 20, meta_sel["color"])} {zone_sel}</div>'
        f'<div style="font-size:13px;color:{txt_sub};margin-top:8px;">{meta_sel["desc"]}</div>'
        f'<div style="font-size:13px;color:{txt_main};margin-top:8px;">'
        f'Facteur dominant : <strong style="color:{meta_sel["color"]};">{meta_sel["facteur"]}</strong>'
        f'</div></div>'
        f'<div style="text-align:right;font-size:12px;color:{txt_dim};'
        f'font-family:DM Mono,monospace;line-height:2.0;">'
        f'{"<br>".join(meta_sel["regions"])}</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

    # ══════════════════════════════════════════════════════════════════════════
    # KPIs
    # ══════════════════════════════════════════════════════════════════════════
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpis = [
        (k1, 'wind',        f"{meta_sel['pm25']:.1f}",     'PM2.5 moy.',  'µg/m³',
         th['red'] if meta_sel['pm25'] > 25 else th['amber'] if meta_sel['pm25'] > 15 else th['green']),
        (k2, 'cloud',       f"{meta_sel['dust']:.0f}",     'Dust moy.',   'µg/m³',
         th['red'] if meta_sel['dust'] > 50 else th['amber'] if meta_sel['dust'] > 20 else th['green']),
        (k3, 'thermometer', f"{meta_sel['temp']:.1f}°",    'Temp. max',   'moy.',
         th['coral'] if meta_sel['temp'] > 32 else th['amber']),
        (k4, 'droplets',    f"{meta_sel['precip']:.1f}",   'Précip.',     'mm/jour',
         th['blue'] if meta_sel['precip'] > 4 else th['amber']),
        (k5, 'wind',        f"{meta_sel['harmattan']:.1f}%",'Harmattan',  'fréq.',
         th['red'] if meta_sel['harmattan'] > 5 else th['green']),
        (k6, 'flame',       f"{meta_sel['feux']:.1f}%",    'Feux',        'fréq.',
         th['red'] if meta_sel['feux'] > 2 else th['green']),
    ]
    for col_ui, ico, val, label, unit, color in kpis:
        with col_ui:
            st.markdown(
                f'<div style="background:{bg_card};border:1px solid {color}66;'
                f'border-top:4px solid {color};border-radius:12px;padding:16px 8px;'
                f'text-align:center;box-shadow:0 4px 20px {color}22;">'
                f'<div style="display:flex;justify-content:center;margin-bottom:6px;">'
                f'{_icon(ico, 20, color)}</div>'
                f'<div style="font-size:28px;font-weight:800;color:{color};line-height:1;">{val}</div>'
                f'<div style="font-size:11px;color:{txt_main};margin-top:8px;font-weight:600;'
                f'text-transform:uppercase;letter-spacing:.06em;">{label}</div>'
                f'<div style="font-size:10px;color:{txt_dim};margin-top:3px;">{unit}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='margin:20px 0 8px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # INSIGHT + QUE FAIRE
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
            f'<div style="background:{bg_card};border:1px solid {meta_sel["color"]}55;'
            f'border-radius:12px;padding:16px 20px;min-height:380px;overflow-y:auto;">'

            f'<div style="font-size:15px;font-weight:700;color:{meta_sel["color"]};'
            f'margin-bottom:16px;display:flex;align-items:center;gap:8px;">'
            f'{_icon(meta_sel["icon"], 18, meta_sel["color"])} Insight — {zone_sel}</div>'

            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;'
            f'padding:10px;background:rgba({rv},{gv},{bv},0.12);border-radius:8px;">'
            f'<div style="flex-shrink:0;">{_icon("trending-up", 24, th["red"])}</div>'
            f'<div>'
            f'<div style="font-size:11px;color:{txt_dim};text-transform:uppercase;letter-spacing:.06em;">Pic saisonnier</div>'
            f'<div style="font-size:18px;font-weight:700;color:{th["red"]};">{MOIS[pic_mois-1]} · {pic_val:.1f} µg/m³</div>'
            f'<div style="font-size:12px;color:{txt_sub};">{(pic_val/15):.1f}x le seuil OMS</div>'
            f'</div></div>'

            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;'
            f'padding:10px;background:rgba(16,185,129,0.12);border-radius:8px;">'
            f'<div style="flex-shrink:0;">{_icon("trending-down", 24, th["green"])}</div>'
            f'<div>'
            f'<div style="font-size:11px;color:{txt_dim};text-transform:uppercase;letter-spacing:.06em;">Minimum saisonnier</div>'
            f'<div style="font-size:18px;font-weight:700;color:{th["green"]};">{MOIS[bas_mois-1]} · {bas_val:.1f} µg/m³</div>'
            f'<div style="font-size:12px;color:{txt_sub};">{"Conforme OMS" if bas_val <= 15 else "Dépasse OMS"}</div>'
            f'</div></div>'

            f'<div style="display:flex;align-items:center;gap:12px;'
            f'padding:10px;background:rgba({rv},{gv},{bv},0.10);border-radius:8px;">'
            f'<div style="flex-shrink:0;">{_icon("zap", 24, meta_sel["color"])}</div>'
            f'<div>'
            f'<div style="font-size:11px;color:{txt_dim};text-transform:uppercase;letter-spacing:.06em;">Amplitude saisonnière</div>'
            f'<div style="font-size:18px;font-weight:700;color:{meta_sel["color"]};">{amplitude:.1f} µg/m³</div>'
            f'<div style="font-size:12px;color:{txt_sub};">{meta_sel["facteur"]}</div>'
            f'</div></div>'

            f'<div style="font-size:9px;color:{txt_dim};margin-top:12px;font-family:DM Mono,monospace;">'
            f'Réf. {meta_sel["ref"]} · INS Cameroun (2019)</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col_rec:
        profil_key = 'citoyen'
        if profil and hasattr(profil, 'lower'):
            p = profil.lower()
            if 'med' in p or 'sant' in p:     profil_key = 'medecin'
            elif 'mai' in p or 'dec' in p:    profil_key = 'maire'
            elif 'cherch' in p or 'res' in p: profil_key = 'chercheur'

        profil_labels = {
            'citoyen':   'Citoyen',
            'medecin':   'Médecin / Soignant',
            'maire':     'Maire / Décideur',
            'chercheur': 'Chercheur / Scientifique',
        }
        profil_icons = {
            'citoyen':   'user',
            'medecin':   'stethoscope',
            'maire':     'landmark',
            'chercheur': 'microscope',
        }

        recos = RECO.get(zone_sel, {}).get(profil_key, [])
        reco_html = ''.join([
            f'<div style="display:flex;align-items:flex-start;gap:10px;'
            f'padding:10px 12px;margin-bottom:8px;'
            f'background:rgba({rv},{gv},{bv},0.10);'
            f'border:1px solid {meta_sel["color"]}33;border-radius:8px;">'
            f'<div style="flex-shrink:0;margin-top:2px;">{_icon(ico, 16, meta_sel["color"])}</div>'
            f'<div style="font-size:13px;color:{txt_sub};line-height:1.7;">{txt}</div>'
            f'</div>'
            for ico, txt in recos
        ])

        st.markdown(
            f'<div style="background:{bg_card};border:1px solid {meta_sel["color"]}55;'
            f'border-radius:12px;padding:16px 20px;min-height:380px;overflow-y:auto;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
            f'<div style="font-size:15px;font-weight:700;color:{meta_sel["color"]};'
            f'display:flex;align-items:center;gap:8px;">'
            f'{_icon(meta_sel["icon"], 18, meta_sel["color"])} Que faire ?</div>'
            f'<div style="font-size:10px;color:{txt_dim};font-family:DM Mono,monospace;'
            f'background:rgba({rv},{gv},{bv},0.20);padding:3px 10px;border-radius:20px;'
            f'display:flex;align-items:center;gap:6px;">'
            f'{_icon(profil_icons[profil_key], 12, txt_dim)} {profil_labels[profil_key]}</div>'
            f'</div>'
            f'{reco_html}'
            f'<div style="font-size:9px;color:{txt_dim};margin-top:10px;font-family:DM Mono,monospace;">'
            f'Basées sur · WHO AQG 2021 · INS Cameroun (2019) · {annees}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin:20px 0 8px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # COMPARAISON DES INDICATEURS
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{txt_main};'
        f'margin-bottom:14px;display:flex;align-items:center;gap:8px;">'
        f'{_icon("bar-chart-2", 16, th["teal"])} Comparaison détaillée des indicateurs — 3 zones'
        f'</div>',
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
            name=nom_zone.replace('Zone ', ''),
            x=list(indicateurs.keys()),
            y=[meta[k] for k in indicateurs.values()],
            marker=dict(
                color=f'rgba({rv2},{gv2},{bv2},{0.90 if is_sel else 0.45})',
                line=dict(width=2 if is_sel else 0,
                          color=meta['color'] if is_sel else f'rgba({rv2},{gv2},{bv2},0)')
            ),
            text=[f'{meta[k]:.1f}' for k in indicateurs.values()],
            textposition='outside',
            textfont=dict(size=13 if is_sel else 11,
                          color=meta['color'] if is_sel else f'rgba({rv2},{gv2},{bv2},0.85)'),
            hovertemplate=f"<b>{nom_zone}</b><br>%{{x}} : %{{y:.1f}}<extra></extra>",
        ))

    fig_bars.add_shape(
        type='line', x0=-0.5, x1=0.5, y0=15, y1=15,
        line=dict(color=th['red'], width=1.5, dash='dash'),
    )
    fig_bars.add_annotation(
        x=0, y=15, text="OMS 15", showarrow=False,
        font=dict(color=th['red'], size=11), yshift=10
    )
    fig_bars.update_layout(
        **PL, height=300, barmode='group',
        margin=dict(l=20, r=20, t=50, b=20),
        uniformtext_minsize=9, uniformtext_mode='hide',
        legend=dict(font=dict(color=txt_sub, size=13),
                    bgcolor='rgba(15,23,42,0.95)',
                    orientation='h', yanchor='top', y=1.18, xanchor='left', x=0),
        xaxis=dict(**GRID, tickfont=dict(size=13, color=txt_main)),
        yaxis=dict(**GRID, tickfont=dict(size=12, color=txt_main)),
    )
    st.plotly_chart(fig_bars, width="stretch")

    # ── Sources ───────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    sources_bar(
        'INS Cameroun (2019) · WHO AQG 2021 · IPCC AR5 (2014) · '
        'Chen & Hoek (2020) · Schepanski et al. (2007) · Knippertz et al. (2008) · '
        'Gordon et al. (2023) PMC9884662 · Barker et al. (2020)',
        th
    )