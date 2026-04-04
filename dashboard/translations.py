"""
translations.py — AirSentinel Cameroun
Tout le texte de l'application en français et en anglais.
Usage : T = get_translations(lang)  puis  T["sidebar_profile"]
"""

TRANSLATIONS = {

    # ══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════════════════════
    "sidebar_app_subtitle": {
        "fr": "CAMEROUN",
        "en": "CAMEROON",
    },
    "sidebar_settings_title": {
        "fr": "PARAMÈTRES",
        "en": "SETTINGS",
    },
    "sidebar_theme_title": {
        "fr": "🎨 THÈME",
        "en": "🎨 THEME",
    },
    "sidebar_lang_title": {
        "fr": "🌐 LANGUE",
        "en": "🌐 LANGUAGE",
    },
    "sidebar_theme_label": {
        "fr": "🎨 Thème",
        "en": "🎨 Theme",
    },
    "sidebar_theme_dark": {
        "fr": "🌙 Sombre",
        "en": "🌙 Dark",
    },
    "sidebar_theme_light": {
        "fr": "☀️ Clair",
        "en": "☀️ Light",
    },
    "sidebar_lang_label": {
        "fr": "🌐 Langue",
        "en": "🌐 Language",
    },
    "sidebar_profile_title": {
        "fr": "MON PROFIL",
        "en": "MY PROFILE",
    },
    "sidebar_profile_citizen": {
        "fr": "👤 Citoyen",
        "en": "👤 Citizen",
    },
    "sidebar_profile_health": {
        "fr": "🩺 Professionnel de santé",
        "en": "🩺 Health professional",
    },
    "sidebar_profile_mayor": {
        "fr": "🏛️ Décideur / Maire",
        "en": "🏛️ Decision maker / Mayor",
    },
    "sidebar_profile_researcher": {
        "fr": "🔬 Chercheur",
        "en": "🔬 Researcher",
    },
    "sidebar_filters_title": {
        "fr": "FILTRES GLOBAUX",
        "en": "GLOBAL FILTERS",
    },
    "sidebar_city_label": {
        "fr": "🏙️ Ville",
        "en": "🏙️ City",
    },
    "sidebar_city_all": {
        "fr": "(Toutes)",
        "en": "(All)",
    },
    "sidebar_region_label": {
        "fr": "🗺️ Région",
        "en": "🗺️ Region",
    },
    "sidebar_region_all": {
        "fr": "(Toutes)",
        "en": "(All)",
    },
    "sidebar_period_label": {
        "fr": "📅 Période",
        "en": "📅 Period",
    },
    "sidebar_active_filters": {
        "fr": "Filtres actifs",
        "en": "Active filters",
    },
    "sidebar_no_filter": {
        "fr": "Aucun filtre — toutes les données",
        "en": "No filter — all data",
    },
    "sidebar_footer": {
        "fr": "IndabaX Cameroon 2026\nDPA Green Tech · ISSEA · ENSP\n17 mars → 7 avril 2026",
        "en": "IndabaX Cameroon 2026\nDPA Green Tech · ISSEA · ENSP\nMarch 17 → April 7, 2026",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════════════════════════════════════
    "header_title": {
        "fr": "AirSentinel Cameroun — Système d'aide à la décision sanitaire",
        "en": "AirSentinel Cameroon — AI-powered health decision support system",
    },
    "header_subtitle": {
        "fr": "42 villes · 10 régions · 87 240 observations · 2020–2025 · XGBoost + Prophet + IRS par ACP",
        "en": "42 cities · 10 regions · 87,240 observations · 2020–2025 · XGBoost + Prophet + HRI by PCA",
    },
    "header_pill_profile": {
        "fr": "Profil",
        "en": "Profile",
    },
    "header_pill_pm25": {
        "fr": "PM2.5 moy.",
        "en": "Avg PM2.5",
    },
    "header_pill_irs": {
        "fr": "IRS",
        "en": "HRI",
    },
    "header_pill_scope": {
        "fr": "Scope",
        "en": "Scope",
    },
    "header_pill_source": {
        "fr": "Source",
        "en": "Source",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════════════════
    "tab_carte": {
        "fr": "🗺️  Carte interactive",
        "en": "🗺️  Interactive map",
    },
    "tab_kpis": {
        "fr": "📊  Indicateurs KPIs",
        "en": "📊  Key indicators",
    },
    "tab_predictions": {
        "fr": "🔮  Prédictions",
        "en": "🔮  Predictions",
    },
    "tab_alertes": {
        "fr": "🚨  Alertes",
        "en": "🚨  Alerts",
    },
    "tab_decision": {
        "fr": "🏥  Décision santé",
        "en": "🏥  Health decisions",
    },
    "tab_contexte": {
        "fr": "🌦️  Contexte",
        "en": "🌦️  Context",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # BLOC 1 — CARTE
    # ══════════════════════════════════════════════════════════════════════════
    "bloc1_label": {
        "fr": "Bloc 1 — Carte interactive",
        "en": "Block 1 — Interactive map",
    },
    "bloc1_subtitle": {
        "fr": "PM2.5 · IRS · Épisodes climatiques · Données 2020–2025",
        "en": "PM2.5 · HRI · Climate episodes · 2020–2025 data",
    },
    "bloc1_all_cities": {
        "fr": "42 villes",
        "en": "42 cities",
    },
    "bloc1_city_prefix": {
        "fr": "Ville : ",
        "en": "City: ",
    },
    "bloc1_map_title": {
        "fr": "PM2.5 moyen",
        "en": "Average PM2.5",
    },
    "bloc1_satellite_label": {
        "fr": "Vue satellite",
        "en": "Satellite view",
    },
    "bloc1_satellite_desc": {
        "fr": "Cameroun · Afrique centrale",
        "en": "Cameroon · Central Africa",
    },
    "bloc1_oms_title": {
        "fr": "Seuils OMS 2021",
        "en": "WHO 2021 thresholds",
    },
    "bloc1_oms_conform": {
        "fr": "Conforme OMS AQG",
        "en": "WHO AQG compliant",
    },
    "bloc1_oms_exceeds": {
        "fr": "Dépasse AQG",
        "en": "Exceeds AQG",
    },
    "bloc1_cities_above": {
        "fr": "villes > OMS",
        "en": "cities > WHO",
    },
    "bloc1_period": {
        "fr": "période",
        "en": "period",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # BLOC 2 — KPIs
    # ══════════════════════════════════════════════════════════════════════════
    "bloc2_label": {
        "fr": "Bloc 2 — Indicateurs clés",
        "en": "Block 2 — Key indicators",
    },
    "bloc2_kpi_pm25_label": {
        "fr": "PM2.5 moyen",
        "en": "Avg PM2.5",
    },
    "bloc2_kpi_pm25_sub": {
        "fr": "OMS 15 µg/m³",
        "en": "WHO 15 µg/m³",
    },
    "bloc2_kpi_irs_label": {
        "fr": "IRS moyen",
        "en": "Avg HRI",
    },
    "bloc2_kpi_irs_sub": {
        "fr": "Niveau : {level} · ACP",
        "en": "Level: {level} · PCA",
    },
    "bloc2_kpi_cities_label": {
        "fr": "Villes > OMS",
        "en": "Cities > WHO",
    },
    "bloc2_kpi_pollutant_label": {
        "fr": "Polluant dominant",
        "en": "Dominant pollutant",
    },
    "bloc2_kpi_pollutant_sub": {
        "fr": "Source principale",
        "en": "Main source",
    },
    "bloc2_kpi_trend_label": {
        "fr": "Tendance vs {year}",
        "en": "Trend vs {year}",
    },
    "bloc2_kpi_trend_sub": {
        "fr": "µg/m³ variation {y1} → {y2}",
        "en": "µg/m³ change {y1} → {y2}",
    },
    "bloc2_kpi_obs_label": {
        "fr": "Observations",
        "en": "Observations",
    },
    "bloc2_kpi_obs_sub": {
        "fr": "jours",
        "en": "days",
    },
    "bloc2_chart1_title": {
        "fr": "PM2.5 mensuel",
        "en": "Monthly PM2.5",
    },
    "bloc2_chart2_title": {
        "fr": "Distribution IRS · Seuils percentiles",
        "en": "HRI distribution · Percentile thresholds",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # BLOC 3 — PRÉDICTIONS
    # ══════════════════════════════════════════════════════════════════════════
    "bloc3_label": {
        "fr": "Bloc 3 — Prédictions",
        "en": "Block 3 — Predictions",
    },
    "bloc3_subtitle": {
        "fr": "Court terme 24h–72h · Simulateur IRS · Calendrier mensuel",
        "en": "Short term 24h–72h · HRI simulator · Monthly calendar",
    },
    "bloc3_tab_short": {
        "fr": "⚡ Court terme 24h–72h",
        "en": "⚡ Short term 24h–72h",
    },
    "bloc3_tab_sim": {
        "fr": "📅 Simulateur IRS",
        "en": "📅 HRI Simulator",
    },
    "bloc3_tab_monthly": {
        "fr": "📆 Calendrier mensuel",
        "en": "📆 Monthly calendar",
    },
    "bloc3_city_select": {
        "fr": "Ville pour la prédiction 72h",
        "en": "City for 72h prediction",
    },
    "bloc3_history_label": {
        "fr": "Historique",
        "en": "Historical data",
    },
    "bloc3_pred_label": {
        "fr": "Prédiction 72h",
        "en": "72h prediction",
    },
    "bloc3_conf_label": {
        "fr": "Intervalle de confiance",
        "en": "Confidence interval",
    },
    "bloc3_sim_intro": {
        "fr": "Valeurs pré-remplies avec les moyennes de",
        "en": "Pre-filled with averages from",
    },
    "bloc3_temp": {
        "fr": "Température max (°C)",
        "en": "Max temperature (°C)",
    },
    "bloc3_wind": {
        "fr": "Vitesse vent (km/h)",
        "en": "Wind speed (km/h)",
    },
    "bloc3_humidity": {
        "fr": "Humidité (%)",
        "en": "Humidity (%)",
    },
    "bloc3_dust": {
        "fr": "Dust µg/m³",
        "en": "Dust µg/m³",
    },
    "bloc3_harmattan": {
        "fr": "🏜️ Harmattan actif",
        "en": "🏜️ Active harmattan",
    },
    "bloc3_fire": {
        "fr": "🔥 Épisode feux",
        "en": "🔥 Fire episode",
    },
    "bloc3_sim_irs": {
        "fr": "IRS simulé",
        "en": "Simulated HRI",
    },
    "bloc3_sim_pm25": {
        "fr": "PM2.5 estimé",
        "en": "Estimated PM2.5",
    },
    "bloc3_sim_avg": {
        "fr": "Moy.",
        "en": "Avg.",
    },
    "bloc3_monthly_title": {
        "fr": "PM2.5 mensuel moyen",
        "en": "Average monthly PM2.5",
    },
    "bloc3_year_select": {
        "fr": "Année à afficher",
        "en": "Year to display",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # BLOC 4 — ALERTES
    # ══════════════════════════════════════════════════════════════════════════
    "bloc4_label": {
        "fr": "Bloc 4 — Alertes automatiques",
        "en": "Block 4 — Automatic alerts",
    },
    "bloc4_feux_title": {
        "fr": "Feux de brousse",
        "en": "Bushfires",
    },
    "bloc4_feux_sub": {
        "fr": "CO > p90 en saison sèche · Barker et al. 2020",
        "en": "CO > p90 in dry season · Barker et al. 2020",
    },
    "bloc4_chaleur_title": {
        "fr": "Vague de chaleur",
        "en": "Heat wave",
    },
    "bloc4_chaleur_sub": {
        "fr": "Temp. > p90 pendant 3 jours · Ceccherini et al. 2017",
        "en": "Temp. > p90 for 3 days · Ceccherini et al. 2017",
    },
    "bloc4_current_badge": {
        "fr": "ACTUEL",
        "en": "CURRENT",
    },
    "bloc4_chart_title": {
        "fr": "Jours par niveau IRS",
        "en": "Days per HRI level",
    },
    # Messages par niveau et par profil
    "bloc4_msg_faible_citizen":     {"fr": "✅ Air sain — sortez normalement",                          "en": "✅ Clean air — go out normally"},
    "bloc4_msg_faible_health":      {"fr": "Flux de consultations normal attendu",                       "en": "Normal consultation flow expected"},
    "bloc4_msg_faible_mayor":       {"fr": "Aucune action requise",                                      "en": "No action required"},
    "bloc4_msg_faible_researcher":  {"fr": "< p50 — médiane historique",                                 "en": "< p50 — historical median"},
    "bloc4_msg_modere_citizen":     {"fr": "⚠️ Groupes sensibles : réduire l'exposition",                "en": "⚠️ Sensitive groups: reduce exposure"},
    "bloc4_msg_modere_health":      {"fr": "Surveiller les patients asthmatiques",                       "en": "Monitor asthmatic patients"},
    "bloc4_msg_modere_mayor":       {"fr": "Informer les établissements scolaires",                      "en": "Inform schools and institutions"},
    "bloc4_msg_modere_researcher":  {"fr": "p50–p75 — pire que 50% des jours observés",                 "en": "p50–p75 — worse than 50% of observed days"},
    "bloc4_msg_eleve_citizen":      {"fr": "🚨 Restez à l'intérieur si possible",                       "en": "🚨 Stay indoors if possible"},
    "bloc4_msg_eleve_health":       {"fr": "Préparer les médicaments respiratoires",                     "en": "Prepare respiratory medications"},
    "bloc4_msg_eleve_mayor":        {"fr": "Annuler les événements sportifs extérieurs",                 "en": "Cancel outdoor sports events"},
    "bloc4_msg_eleve_researcher":   {"fr": "p75–p90 — pire que 75% · PM2.5 > OMS",                      "en": "p75–p90 — worse than 75% · PM2.5 > WHO"},
    "bloc4_msg_critique_citizen":   {"fr": "🔴 DANGER CRITIQUE — masques obligatoires",                 "en": "🔴 CRITICAL DANGER — masks required"},
    "bloc4_msg_critique_health":    {"fr": "URGENCE : activer le protocole sanitaire",                   "en": "EMERGENCY: activate health protocol"},
    "bloc4_msg_critique_mayor":     {"fr": "SMS d'alerte · Plan communal sanitaire",                     "en": "Alert SMS · Community health plan"},
    "bloc4_msg_critique_researcher":{"fr": "≥ p90 — pire que 90% des jours historiques",                "en": "≥ p90 — worse than 90% of historical days"},
    # Labels niveaux
    "level_faible":   {"fr": "FAIBLE",   "en": "LOW"},
    "level_modere":   {"fr": "MODÉRÉ",   "en": "MODERATE"},
    "level_eleve":    {"fr": "ÉLEVÉ",    "en": "HIGH"},
    "level_critique": {"fr": "CRITIQUE", "en": "CRITICAL"},

    # ══════════════════════════════════════════════════════════════════════════
    # BLOC 5 — DÉCISION SANTÉ
    # ══════════════════════════════════════════════════════════════════════════
    "bloc5_label": {
        "fr": "Bloc 5 — Aide à la décision sanitaire",
        "en": "Block 5 — Health decision support",
    },
    "bloc5_innovation": {
        "fr": "Notre innovation · Aucune autre équipe ne propose ça",
        "en": "Our innovation · No other team offers this",
    },
    "bloc5_innovation_desc": {
        "fr": "Recommandations basées sur les percentiles IRS calculés par ACP sur les 42 moyennes de villes — pas sur des chiffres arbitraires.",
        "en": "Recommendations based on HRI percentiles computed by PCA on 42 city averages — not arbitrary thresholds.",
    },
    "bloc5_slider_label": {
        "fr": "Simuler une valeur IRS",
        "en": "Simulate an HRI value",
    },
    "bloc5_rec_header": {
        "fr": "Recommandations",
        "en": "Recommendations",
    },
    "bloc5_med_label":    {"fr": "💊 Médicaments",      "en": "💊 Medications"},
    "bloc5_cons_label":   {"fr": "🏥 Consultations",    "en": "🏥 Consultations"},
    "bloc5_action_label": {"fr": "⚡ Action immédiate", "en": "⚡ Immediate action"},
    # Statuts professionnels
    "bloc5_status_normal":  {"fr": "Normal",       "en": "Normal"},
    "bloc5_status_watch":   {"fr": "Vigilance",    "en": "Watch"},
    "bloc5_status_high":    {"fr": "Risque élevé", "en": "High risk"},
    "bloc5_status_urgent":  {"fr": "URGENCE",      "en": "EMERGENCY"},
    "bloc5_status_calm":    {"fr": "Calme",        "en": "Calm"},
    "bloc5_status_alert":   {"fr": "Alerte",       "en": "Alert"},
    "bloc5_status_crisis":  {"fr": "CRISE",        "en": "CRISIS"},
    # Messages santé pro
    "bloc5_med_normal":    {"fr": "Stock habituel suffisant",                      "en": "Regular stock sufficient"},
    "bloc5_med_watch":     {"fr": "Surveiller les stocks de bronchodilatateurs",   "en": "Monitor bronchodilator stocks"},
    "bloc5_med_high":      {"fr": "Préparer les médicaments respiratoires",        "en": "Prepare respiratory medications"},
    "bloc5_med_urgent":    {"fr": "COMMANDER EN URGENCE : bronchodilatateurs",     "en": "ORDER URGENTLY: bronchodilators"},
    "bloc5_cons_normal":   {"fr": "Flux de consultations normal attendu",          "en": "Normal consultation flow expected"},
    "bloc5_cons_watch":    {"fr": "Légère hausse possible dans 24–72h",            "en": "Slight increase possible within 24–72h"},
    "bloc5_cons_high":     {"fr": "Pire que 75% des jours historiques",            "en": "Worse than 75% of historical days"},
    "bloc5_cons_urgent":   {"fr": "Pire que 90% des jours historiques",            "en": "Worse than 90% of historical days"},
    "bloc5_action_normal": {"fr": "Aucune action préventive requise",              "en": "No preventive action required"},
    "bloc5_action_watch":  {"fr": "Contacter les patients asthmatiques connus",    "en": "Contact known asthmatic patients"},
    "bloc5_action_high":   {"fr": "Appeler du personnel de renfort",               "en": "Call for additional staff"},
    "bloc5_action_urgent": {"fr": "Activer le protocole d'urgence sanitaire",      "en": "Activate emergency health protocol"},
    # Messages maire
    "bloc5_mayor_normal":  {"fr": [ "Aucune action requise"],                                                         "en": [ "No action required"]},
    "bloc5_mayor_watch":   {"fr": [ "Informer les établissements scolaires", "Publier un bulletin préventif"],          "en": [ "Inform schools", "Publish a preventive bulletin"]},
    "bloc5_mayor_high":    {"fr": [ "Annuler événements sportifs ext.", "Envoyer SMS préventif", "Contacter directeurs"], "en": [ "Cancel outdoor sports events", "Send preventive SMS", "Contact school principals"]},
    "bloc5_mayor_urgent":  {"fr": [ "SMS d'urgence aux habitants", "Activer plan communal sanitaire", "Fermer les écoles", "Communiqué de presse immédiat"], "en": [ "Emergency SMS to residents", "Activate community health plan", "Close schools", "Immediate press release"]},
    # Messages citoyen
    "bloc5_citizen_faible":   {"fr": "✅ Air sain — sortez normalement",                          "en": "✅ Clean air — go out normally"},
    "bloc5_citizen_modere":   {"fr": "⚠️ Réduisez les activités intenses en extérieur",           "en": "⚠️ Reduce intense outdoor activities"},
    "bloc5_citizen_eleve":    {"fr": "🚨 Restez à l'intérieur si possible",                       "en": "🚨 Stay indoors if possible"},
    "bloc5_citizen_critique": {"fr": "🔴 DANGER — restez à l'intérieur, masque recommandé",       "en": "🔴 DANGER — stay indoors, mask recommended"},
    # Messages chercheur
    "bloc5_researcher_faible":   {"fr": "IRS < p50 — médiane historique",  "en": "HRI < p50 — historical median"},
    "bloc5_researcher_modere":   {"fr": "p50–p75 — pire que 50% des jours", "en": "p50–p75 — worse than 50% of days"},
    "bloc5_researcher_eleve":    {"fr": "p75–p90 — pire que 75% · PM2.5 > 15 µg/m³ (OMS)", "en": "p75–p90 — worse than 75% · PM2.5 > 15 µg/m³ (WHO)"},
    "bloc5_researcher_critique": {"fr": "≥ p90 — situation exceptionnelle", "en": "≥ p90 — exceptional situation"},

    # ══════════════════════════════════════════════════════════════════════════
    # BLOC 6 — CONTEXTE
    # ══════════════════════════════════════════════════════════════════════════
    "bloc6_label": {
        "fr": "Bloc 6 — Contexte",
        "en": "Block 6 — Context",
    },
    "bloc6_subtitle": {
        "fr": "Polluant dominant · Comparaison N-1 · Épisodes par zone · UV & Ozone",
        "en": "Dominant pollutant · N-1 comparison · Episodes by zone · UV & Ozone",
    },
    "bloc6_chart1_title": {
        "fr": "Polluant dominant",
        "en": "Dominant pollutant",
    },
    "bloc6_chart2_prefix": {
        "fr": "PM2.5 · {y1} vs {y2}",
        "en": "PM2.5 · {y1} vs {y2}",
    },
    "bloc6_chart3_title": {
        "fr": "Épisodes climatiques par zone (p90)",
        "en": "Climate episodes by zone (p90)",
    },
    "bloc6_seasons_title": {
        "fr": "Contexte saisonnier · Cameroun",
        "en": "Seasonal context · Cameroon",
    },
    "bloc6_uv_title": {
        "fr": "UV & Ozone · UV élevé → ozone secondaire",
        "en": "UV & Ozone · High UV → secondary ozone",
    },
    "bloc6_harmattan_label": {"fr": "Harmattan", "en": "Harmattan"},
    "bloc6_fire_label":      {"fr": "Feux",      "en": "Fires"},
    "bloc6_heat_label":      {"fr": "Chaleur",   "en": "Heat"},
    # Saisons
    "season1_periode": {"fr": "Nov → Fév", "en": "Nov → Feb"},
    "season1_titre":   {"fr": "Saison sèche — Harmattan", "en": "Dry season — Harmattan"},
    "season1_detail":  {"fr": "Poussières sahariennes · CO élevé · PM2.5 ↑", "en": "Saharan dust · High CO · PM2.5 ↑"},
    "season2_periode": {"fr": "Mar → Mai", "en": "Mar → May"},
    "season2_titre":   {"fr": "Début saison des pluies",  "en": "Start of rainy season"},
    "season2_detail":  {"fr": "Nettoyage atmosphérique · PM2.5 ↓", "en": "Atmospheric cleaning · PM2.5 ↓"},
    "season3_periode": {"fr": "Jun → Sep", "en": "Jun → Sep"},
    "season3_titre":   {"fr": "Saison des pluies",         "en": "Rainy season"},
    "season3_detail":  {"fr": "Humidité infectieuse p90 · Ozone secondaire ↓", "en": "Infectious humidity p90 · Secondary ozone ↓"},
    "season4_periode": {"fr": "Oct → Nov", "en": "Oct → Nov"},
    "season4_titre":   {"fr": "Transition · Feux de brousse", "en": "Transition · Bushfires"},
    "season4_detail":  {"fr": "CO traceur · PM2.5 ↑↑ zones sahéliennes", "en": "CO tracer · PM2.5 ↑↑ Sahelian zones"},

    # ══════════════════════════════════════════════════════════════════════════
    # COMMUNS
    # ══════════════════════════════════════════════════════════════════════════
    "irs_name": {
        "fr": "IRS",
        "en": "HRI",
    },
    "irs_full": {
        "fr": "Indice de Risque Sanitaire",
        "en": "Health Risk Index",
    },
    "who_threshold": {
        "fr": "Seuil OMS",
        "en": "WHO threshold",
    },
    "all_cities": {
        "fr": "Toutes villes",
        "en": "All cities",
    },
    "all_regions": {
        "fr": "Toutes régions",
        "en": "All regions",
    },
    "no_data": {
        "fr": "Aucune donnée pour ce filtre — élargissez la sélection.",
        "en": "No data for this filter — please broaden your selection.",
    },
    "sources_who":    {"fr": "Seuils : WHO AQG 2021 (NCBI NBK574591)", "en": "Thresholds: WHO AQG 2021 (NCBI NBK574591)"},
    "sources_cecc":   {"fr": "Ceccherini et al. 2017",                 "en": "Ceccherini et al. 2017"},
    "sources_barker": {"fr": "Barker et al. 2020",                     "en": "Barker et al. 2020"},
    "sources_bauer":  {"fr": "Bauer et al. 2024 (PMC11523266)",        "en": "Bauer et al. 2024 (PMC11523266)"},
    "airsentinel_tag":{"fr": "AirSentinel · IndabaX 2026",             "en": "AirSentinel · IndabaX 2026"},
    "mois": {
        "fr": ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"],
        "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # LANDING PAGE
    # ══════════════════════════════════════════════════════════════════════════
    "landing_subtitle": {
        "fr": "CAMEROUN",
        "en": "CAMEROON",
    },
    "landing_slogan": {
        "fr": "Anticiper. Alerter. Protéger.",
        "en": "Anticipate. Alert. Protect.",
    },
    "landing_desc": {
        "fr": "Aide à la décision sanitaire par l'IA<br>40 villes · 10 régions · 50 760 observations",
        "en": "AI health decision support system<br>40 cities · 10 regions · 50,760 observations",
    },
    "landing_count_villes":  {"fr": "villes",      "en": "cities"},
    "landing_count_regions": {"fr": "régions",     "en": "regions"},
    "landing_count_obs":     {"fr": "observations", "en": "observations"},
    "landing_count_pred":    {"fr": "prédictions",  "en": "predictions"},
    "landing_btn_enter": {
        "fr": "🚀  Accéder au Dashboard  →",
        "en": "🚀  Open Dashboard  →",
    },
    "landing_about_btn": {
        "fr": "ℹ️  À Propos",
        "en": "ℹ️  About",
    },
    "landing_confirm_theme": {
        "fr": "Passer en mode {mode} ?",
        "en": "Switch to {mode} mode?",
    },
    "landing_confirm_lang": {
        "fr": "Changer pour l'{lang} ?",
        "en": "Switch to {lang}?",
    },
    "landing_yes": {"fr": "Confirmer", "en": "Confirm"},
    "landing_no": {"fr": "Annuler", "en": "Cancel"},
}


def get_t(lang: str = "fr") -> dict:
    """
    Retourne un dictionnaire T où T["key"] donne directement
    la chaîne dans la langue demandée.
    Usage : T = get_t(lang) ; T["header_title"]
    """
    return {k: (v[lang] if isinstance(v, dict) and lang in v else v)
            for k, v in TRANSLATIONS.items()}
