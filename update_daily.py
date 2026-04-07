"""
=============================================================================
 AirSentinel Cameroun — Équipe DPA Green Tech
 Hackathon IndabaX Cameroon 2026
=============================================================================
 SCRIPT : update_daily.py
 Mise à jour quotidienne automatique du dataset_final.xlsx

 Ce script :
   1. Télécharge les données météo + pollution d'aujourd'hui (Open-Meteo)
   2. Calcule toutes les variables dérivées (lags, IRS, épisodes...)
   3. Ajoute les nouvelles lignes dans dataset_final.xlsx
   4. Traite automatiquement les valeurs manquantes

 UTILISATION :
   python update_daily.py

 AUTOMATISATION (GitHub Actions) :
   Voir .github/workflows/update_daily.yml
=============================================================================
"""

import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import numpy as np
import joblib
import time
import os
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# Chemins
PATH_DATASET = 'data/processed/dataset_final.xlsx'

# Date à télécharger — aujourd'hui
AUJOURD_HUI = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

print(f'📅 Mise à jour pour le : {AUJOURD_HUI}')

# APIs Open-Meteo
URL_METEO = 'https://api.open-meteo.com/v1/forecast'
URL_POLL  = 'https://air-quality-api.open-meteo.com/v1/air-quality'

# Variables météo à télécharger (journalières)
VARS_METEO = [
    'weather_code',
    'temperature_2m_max',
    'temperature_2m_min',
    'temperature_2m_mean',
    'apparent_temperature_max',
    'apparent_temperature_min',
    'apparent_temperature_mean',
    'sunrise',
    'sunset',
    'daylight_duration',
    'sunshine_duration',
    'precipitation_sum',
    'rain_sum',
    'snowfall_sum',
    'precipitation_hours',
    'wind_speed_10m_max',
    'wind_gusts_10m_max',
    'wind_direction_10m_dominant',
    'shortwave_radiation_sum',
    'et0_fao_evapotranspiration',
]

# Variables pollution à télécharger (horaires → agrégées en journalier)
VARS_POLL = [
    'pm2_5',
    'pm10',
    'nitrogen_dioxide',
    'sulphur_dioxide',
    'ozone',
    'carbon_monoxide',
    'dust',
    'uv_index',
    'us_aqi',
    'us_aqi_pm2_5',
    'us_aqi_pm10',
    'us_aqi_nitrogen_dioxide',
    'us_aqi_ozone',
    'us_aqi_sulphur_dioxide',
    'us_aqi_carbon_monoxide',
]

# Seuils PM2.5 OMS AQG 2021 — pour calcul de l'IRS
# Référence : WHO AQG 2021 — NCBI NBK574591, Table 3.6
SEUIL_AQG = 15.0   # AQG — objectif final OMS
SEUIL_IT4 = 25.0   # Interim Target 4
SEUIL_IT3 = 37.5   # Interim Target 3
SEUIL_IT2 = 50.0   # Interim Target 2
SEUIL_IT1 = 75.0   # Interim Target 1

# Temps d'attente entre les villes (éviter limite API)
TEMPS_ATTENTE = 6

# ─────────────────────────────────────────────────────────────────────────────
# LISTE DES 40 VILLES
# ─────────────────────────────────────────────────────────────────────────────

VILLES_CAMEROUN = [
    # Adamaoua
    {'ville': 'Meiganga',    'region': 'Adamaoua',     'latitude': 6.5167,  'longitude': 14.3000},
    {'ville': 'Ngaoundere',  'region': 'Adamaoua',     'latitude': 7.3167,  'longitude': 13.5833},
    {'ville': 'Tibati',      'region': 'Adamaoua',     'latitude': 6.4667,  'longitude': 12.6333},
    {'ville': 'Tignere',     'region': 'Adamaoua',     'latitude': 7.3667,  'longitude': 12.6500},
    # Centre
    {'ville': 'Akonolinga',  'region': 'Centre',       'latitude': 3.7667,  'longitude': 12.2500},
    {'ville': 'Bafia',       'region': 'Centre',       'latitude': 4.7500,  'longitude': 11.2333},
    {'ville': 'Mbalmayo',    'region': 'Centre',       'latitude': 3.5167,  'longitude': 11.5000},
    {'ville': 'Yaounde',     'region': 'Centre',       'latitude': 3.8667,  'longitude': 11.5167},
    # Est
    {'ville': 'Abong-Mbang', 'region': 'Est',          'latitude': 3.9833,  'longitude': 13.1667},
    {'ville': 'Batouri',     'region': 'Est',          'latitude': 4.4333,  'longitude': 14.3667},
    {'ville': 'Bertoua',     'region': 'Est',          'latitude': 4.5833,  'longitude': 13.6833},
    {'ville': 'Yokadouma',   'region': 'Est',          'latitude': 3.5167,  'longitude': 15.0500},
    # Extrême-Nord
    {'ville': 'Kousseri',    'region': 'Extreme-Nord', 'latitude': 12.0833, 'longitude': 15.0333},
    {'ville': 'Maroua',      'region': 'Extreme-Nord', 'latitude': 10.5833, 'longitude': 14.3167},
    {'ville': 'Mokolo',      'region': 'Extreme-Nord', 'latitude': 10.7333, 'longitude': 13.8000},
    {'ville': 'Yagoua',      'region': 'Extreme-Nord', 'latitude': 10.3333, 'longitude': 15.2333},
    # Littoral
    {'ville': 'Douala',      'region': 'Littoral',     'latitude': 4.0483,  'longitude': 9.7000},
    {'ville': 'Edea',        'region': 'Littoral',     'latitude': 3.8000,  'longitude': 10.1333},
    {'ville': 'Loum',        'region': 'Littoral',     'latitude': 4.7167,  'longitude': 9.7333},
    {'ville': 'Nkongsamba',  'region': 'Littoral',     'latitude': 4.9500,  'longitude': 9.9333},
    # Nord
    {'ville': 'Garoua',      'region': 'Nord',         'latitude': 9.3000,  'longitude': 13.3833},
    {'ville': 'Guider',      'region': 'Nord',         'latitude': 9.9333,  'longitude': 13.9500},
    {'ville': 'Poli',        'region': 'Nord',         'latitude': 8.4833,  'longitude': 13.2333},
    {'ville': 'Touboro',     'region': 'Nord',         'latitude': 7.7667,  'longitude': 15.3667},
    # Nord-Ouest
    {'ville': 'Bamenda',     'region': 'Nord-Ouest',   'latitude': 5.9500,  'longitude': 10.1500},
    {'ville': 'Kumbo',       'region': 'Nord-Ouest',   'latitude': 6.2000,  'longitude': 10.6833},
    {'ville': 'Mbengwi',     'region': 'Nord-Ouest',   'latitude': 6.0167,  'longitude': 10.0000},
    {'ville': 'Wum',         'region': 'Nord-Ouest',   'latitude': 6.3833,  'longitude': 10.0667},
    # Ouest
    {'ville': 'Bafoussam',   'region': 'Ouest',        'latitude': 5.4667,  'longitude': 10.4167},
    {'ville': 'Dschang',     'region': 'Ouest',        'latitude': 5.4500,  'longitude': 10.0500},
    {'ville': 'Foumban',     'region': 'Ouest',        'latitude': 5.7167,  'longitude': 10.9000},
    {'ville': 'Mbouda',      'region': 'Ouest',        'latitude': 5.6333,  'longitude': 10.2500},
    # Sud
    {'ville': 'Ambam',       'region': 'Sud',          'latitude': 2.3833,  'longitude': 11.2833},
    {'ville': 'Ebolowa',     'region': 'Sud',          'latitude': 2.9000,  'longitude': 11.1500},
    {'ville': 'Kribi',       'region': 'Sud',          'latitude': 2.9500,  'longitude': 9.9167},
    {'ville': 'Sangmelima',  'region': 'Sud',          'latitude': 2.9333,  'longitude': 11.9833},
    # Sud-Ouest
    {'ville': 'Buea',        'region': 'Sud-Ouest',    'latitude': 4.1500,  'longitude': 9.2333},
    {'ville': 'Kumba',       'region': 'Sud-Ouest',    'latitude': 4.6333,  'longitude': 9.4500},
    {'ville': 'Limbe',       'region': 'Sud-Ouest',    'latitude': 4.0167,  'longitude': 9.2000},
    {'ville': 'Mamfe',       'region': 'Sud-Ouest',    'latitude': 5.7667,  'longitude': 9.3000},
]

# ─────────────────────────────────────────────────────────────────────────────
# CLIENT OPEN-METEO
# ─────────────────────────────────────────────────────────────────────────────

cache_session    = requests_cache.CachedSession('.cache_daily', expire_after=3600)
retry_session    = retry(cache_session, retries=5, backoff_factor=0.5)
openmeteo_client = openmeteo_requests.Client(session=retry_session)

# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS DE TÉLÉCHARGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def telecharger_meteo_ville(ville_info, date):
    """Télécharge les données météo journalières pour une ville."""
    try:
        params = {
            'latitude':   ville_info['latitude'],
            'longitude':  ville_info['longitude'],
            'daily':      VARS_METEO,
            'start_date': date,
            'end_date':   date,
            'timezone':   'Africa/Douala',
        }
        reponses = openmeteo_client.weather_api(URL_METEO, params=params)
        r        = reponses[0]
        daily    = r.Daily()

        daily_data = {
            'date':      pd.to_datetime(date),
            'ville':     ville_info['ville'],
            'region':    ville_info['region'],
            'latitude':  ville_info['latitude'],
            'longitude': ville_info['longitude'],
        }

        for idx, nom in enumerate(VARS_METEO):
            try:
                val = daily.Variables(idx).ValuesAsNumpy()
                daily_data[nom] = float(val[0]) if len(val) > 0 else np.nan
            except:
                daily_data[nom] = np.nan

        return daily_data

    except Exception as e:
        print(f'      ❌ Météo erreur : {e}')
        return None


def telecharger_pollution_ville(ville_info, date):
    """Télécharge les données pollution horaires et agrège en journalier."""
    try:
        params = {
            'latitude':   ville_info['latitude'],
            'longitude':  ville_info['longitude'],
            'hourly':     VARS_POLL,
            'start_date': date,
            'end_date':   date,
            'timezone':   'Africa/Douala',
        }
        reponses = openmeteo_client.weather_api(URL_POLL, params=params)
        hourly   = reponses[0].Hourly()

        df_h = pd.DataFrame({
            'pm2_5':     hourly.Variables(0).ValuesAsNumpy(),
            'pm10':      hourly.Variables(1).ValuesAsNumpy(),
            'no2':       hourly.Variables(2).ValuesAsNumpy(),
            'so2':       hourly.Variables(3).ValuesAsNumpy(),
            'ozone':     hourly.Variables(4).ValuesAsNumpy(),
            'co':        hourly.Variables(5).ValuesAsNumpy(),
            'dust':      hourly.Variables(6).ValuesAsNumpy(),
            'uv_index':  hourly.Variables(7).ValuesAsNumpy(),
            'us_aqi':    hourly.Variables(8).ValuesAsNumpy(),
            'aqi_pm25':  hourly.Variables(9).ValuesAsNumpy(),
            'aqi_pm10':  hourly.Variables(10).ValuesAsNumpy(),
            'aqi_no2':   hourly.Variables(11).ValuesAsNumpy(),
            'aqi_ozone': hourly.Variables(12).ValuesAsNumpy(),
            'aqi_so2':   hourly.Variables(13).ValuesAsNumpy(),
            'aqi_co':    hourly.Variables(14).ValuesAsNumpy(),
        })

        row_poll = {
            'pm2_5_moyen':  df_h['pm2_5'].mean(),
            'pm2_5_max':    df_h['pm2_5'].max(),
            'pm10_moyen':   df_h['pm10'].mean(),
            'dust_moyen':   df_h['dust'].mean(),
            'co_moyen':     df_h['co'].mean(),
            'no2_moyen':    df_h['no2'].mean(),
            'so2_moyen':    df_h['so2'].mean(),
            'ozone_moyen':  df_h['ozone'].mean(),
            'uv_moyen':     df_h['uv_index'].mean(),
            'us_aqi_moyen': df_h['us_aqi'].mean(),
        }

        # Polluant dominant
        aqi_dict = {
            'PM2.5': df_h['aqi_pm25'].mean(),
            'PM10':  df_h['aqi_pm10'].mean(),
            'NO2':   df_h['aqi_no2'].mean(),
            'Ozone': df_h['aqi_ozone'].mean(),
            'SO2':   df_h['aqi_so2'].mean(),
            'CO':    df_h['aqi_co'].mean(),
        }
        row_poll['polluant_dominant'] = max(aqi_dict, key=aqi_dict.get)

        # Niveau alerte basé sur AQI
        aqi = row_poll['us_aqi_moyen']
        if   aqi <= 50:  row_poll['niveau_alerte'] = 'BON'
        elif aqi <= 100: row_poll['niveau_alerte'] = 'MODÉRÉ'
        elif aqi <= 150: row_poll['niveau_alerte'] = 'MAUVAIS SENSIBLES'
        elif aqi <= 200: row_poll['niveau_alerte'] = 'MAUVAIS'
        elif aqi <= 300: row_poll['niveau_alerte'] = 'TRÈS MAUVAIS'
        else:            row_poll['niveau_alerte'] = 'DANGEREUX'

        return row_poll

    except Exception as e:
        print(f'      ❌ Pollution erreur : {e}')
        return None


# ─────────────────────────────────────────────────────────────────────────────
# CALCUL DES VARIABLES DÉRIVÉES
# ─────────────────────────────────────────────────────────────────────────────

def calculer_variables_derivees(df_new, df_historique, date):
    """
    Calcule toutes les variables dérivées comme dans les notebooks 02→05.
    Nécessite df_historique pour calculer les lags et moyennes glissantes.
    """
    date_ts = pd.Timestamp(date)

    # ── Variables temporelles ─────────────────────────────────────────────
    df_new['annee']      = df_new['date'].dt.year
    df_new['mois']       = df_new['date'].dt.month
    df_new['jour_annee'] = df_new['date'].dt.dayofyear

    # Saison code — INS Cameroun (2019)
    # 0 = saison sèche (nov→mar), 1 = saison pluies (avr→oct)
    def saison(mois):
        return 0 if mois in [11, 12, 1, 2, 3] else 1
    df_new['saison_code'] = df_new['mois'].apply(saison)

    # ── Log PM2.5 ─────────────────────────────────────────────────────────
    df_new['pm2_5_log'] = np.log1p(df_new['pm2_5_moyen'])

    # ── Combinaison historique + nouvelles données pour les lags ──────────
    df_combined = pd.concat([df_historique, df_new], ignore_index=True)
    df_combined = df_combined.sort_values(['ville', 'date']).reset_index(drop=True)

    # ── Lags par ville ────────────────────────────────────────────────────
    df_combined['pm2_5_lag_1j']  = df_combined.groupby('ville')['pm2_5_moyen'].shift(1)
    df_combined['pm2_5_lag_3j']  = df_combined.groupby('ville')['pm2_5_moyen'].shift(3)
    df_combined['pm2_5_lag_7j']  = df_combined.groupby('ville')['pm2_5_moyen'].shift(7)
    df_combined['pm2_5_moy_7j']  = df_combined.groupby('ville')['pm2_5_moyen'].transform(
        lambda x: x.shift(1).rolling(7, min_periods=1).mean()
    )
    df_combined['pm2_5_moy_30j'] = df_combined.groupby('ville')['pm2_5_moyen'].transform(
        lambda x: x.shift(1).rolling(30, min_periods=1).mean()
    )

    # ── Indice de stagnation ──────────────────────────────────────────────
    df_combined['indice_stagnation'] = (
        (df_combined['wind_speed_10m_max'] < df_combined['wind_speed_10m_max'].quantile(0.25)).astype(int) +
        (df_combined['precipitation_sum']  < 1.0).astype(int)
    )

    # ── Épisodes climatiques ──────────────────────────────────────────────
    # harmattan_intense : dust > p90 ET précipitations < p10
    # Référence : Schepanski et al. (2007) + Knippertz et al. (2008)
    seuil_dust  = df_combined.groupby('region')['dust_moyen'].transform(
        lambda x: x.quantile(0.90))
    seuil_pluie = df_combined.groupby('region')['precipitation_sum'].transform(
        lambda x: x.quantile(0.10))
    df_combined['harmattan_intense'] = (
        (df_combined['dust_moyen']        > seuil_dust) &
        (df_combined['precipitation_sum'] < seuil_pluie)
    ).astype(int)

    # episode_feux : CO > p90 en saison sèche
    # Référence : Barker et al. (2020) + Gordon et al. (2023)
    seuil_co = df_combined[df_combined['saison_code'] == 0]['co_moyen'].quantile(0.90)
    df_combined['episode_feux'] = (
        (df_combined['co_moyen']    > seuil_co) &
        (df_combined['saison_code'] == 0)
    ).astype(int)

    # ── Dummies région ────────────────────────────────────────────────────
    regions = ['Adamaoua', 'Centre', 'Est', 'Extreme-Nord',
               'Littoral', 'Nord', 'Nord-Ouest', 'Ouest', 'Sud', 'Sud-Ouest']
    for reg in regions:
        df_combined[f'region_{reg}'] = (df_combined['region'] == reg).astype(int)

# ── IRS — Indice de Risque Sanitaire par ACP ─────────────────────────
    # Référence : Notebook 05 · INS Cameroun (2019)
    def niveau_sanitaire_pm25(pm25):
        if   pm25 <= SEUIL_AQG: return 'FAIBLE'
        elif pm25 <= SEUIL_IT4: return 'MODÉRÉ'
        elif pm25 <= SEUIL_IT3: return 'ÉLEVÉ'
        elif pm25 <= SEUIL_IT2: return 'TRÈS ÉLEVÉ'
        elif pm25 <= SEUIL_IT1: return 'CRITIQUE'
        else:                   return 'DANGEREUX'

    try:
        scaler_irs = joblib.load('models/scaler_acp_irs.pkl')
        pca_irs    = joblib.load('models/pca_irs.pkl')
        cols_irs   = joblib.load('models/cols_irs.pkl')
        seuils_irs = joblib.load('models/seuils_irs.pkl')

        cols_ok  = [c for c in cols_irs if c in df_combined.columns]
        X        = scaler_irs.transform(
                     df_combined[cols_ok].fillna(df_combined[cols_ok].median())
                   )
        scores   = pca_irs.transform(X)

        if pca_irs.n_components_ == 1:
            irs_brut = scores[:, 0]
        else:
            v        = pca_irs.explained_variance_ratio_
            irs_brut = (v[0]*scores[:,0] + v[1]*scores[:,1]) / (v[0]+v[1])

        irs_min = seuils_irs.get('irs_min', irs_brut.min())
        irs_max = seuils_irs.get('irs_max', irs_brut.max())

        df_combined['IRS']              = ((irs_brut - irs_min) / (irs_max - irs_min)).clip(0, 1)
        df_combined['IRS_brut']         = df_combined['IRS']
        df_combined['niveau_sanitaire'] = df_combined['pm2_5_moyen'].apply(niveau_sanitaire_pm25)
        print('✅ IRS calculé par ACP')

    except Exception as e:
        print(f'⚠️ ACP indisponible → fallback seuils OMS : {e}')
        df_combined['IRS_brut']         = df_combined['pm2_5_moyen'].apply(
            lambda pm25: 0 if pm25<=SEUIL_AQG else 1 if pm25<=SEUIL_IT4 else
                         2 if pm25<=SEUIL_IT3 else 3 if pm25<=SEUIL_IT2 else
                         4 if pm25<=SEUIL_IT1 else 5
        )
        df_combined['IRS']              = df_combined['IRS_brut'] / 5.0
        df_combined['niveau_sanitaire'] = df_combined['pm2_5_moyen'].apply(niveau_sanitaire_pm25)

    # ── Récupérer seulement les nouvelles lignes ──────────────────────────
    df_result = df_combined[df_combined['date'] == date_ts].copy()

    return df_result


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAMME PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print('=' * 65)
    print('  AirSentinel Cameroun — Mise à jour quotidienne')
    print(f'  Date : {AUJOURD_HUI}')
    print(f'  Villes : {len(VILLES_CAMEROUN)}')
    print('=' * 65)

    # ── Charger le dataset existant ───────────────────────────────────────
    # Après
    print(f'\n📂 Chargement du parquet...')
    PATH_PARQUET = PATH_DATASET.replace('.xlsx', '.parquet')

    if not os.path.exists(PATH_PARQUET):
        print(f'❌ Fichier parquet introuvable : {PATH_PARQUET}')
        return

    df_historique = pd.read_parquet(PATH_DATASET.replace('.xlsx', '.parquet'))
    df_historique['date'] = pd.to_datetime(df_historique['date'])
    print(f'✅ Dataset chargé : {len(df_historique):,} lignes')

    # Vérifier si les données d'aujourd'hui existent déjà
    date_ts = pd.Timestamp(AUJOURD_HUI)
    if date_ts in df_historique['date'].values:
        print(f'⚠️  Les données du {AUJOURD_HUI} existent déjà — arrêt.')
        return

    # ── Télécharger pour chaque ville ─────────────────────────────────────
    print(f'\n🌍 Téléchargement des données du {AUJOURD_HUI}...\n')
    nouvelles_lignes = []

    for i, ville_info in enumerate(VILLES_CAMEROUN, 1):
        nom = ville_info['ville']
        print(f'  [{i:02d}/{len(VILLES_CAMEROUN)}] {nom}...', end=' ', flush=True)

        # Télécharger météo
        row_meteo = telecharger_meteo_ville(ville_info, AUJOURD_HUI)
        if row_meteo is None:
            print('❌ météo manquante')
            continue

        # Télécharger pollution
        row_poll = telecharger_pollution_ville(ville_info, AUJOURD_HUI)
        if row_poll is None:
            print('❌ pollution manquante')
            continue

        # Fusionner météo + pollution
        row = {**row_meteo, **row_poll}
        nouvelles_lignes.append(row)
        print(f'✅ PM2.5={row["pm2_5_moyen"]:.1f} µg/m³')

        # Pause entre les villes
        if i < len(VILLES_CAMEROUN):
            time.sleep(TEMPS_ATTENTE)

    if not nouvelles_lignes:
        print('\n❌ Aucune donnée téléchargée.')
        return

    print(f'\n✅ {len(nouvelles_lignes)}/40 villes téléchargées')

    # ── Créer DataFrame des nouvelles données ─────────────────────────────
    df_new = pd.DataFrame(nouvelles_lignes)
    df_new['date'] = pd.to_datetime(df_new['date'])

    # Ajouter id
    id_max = df_historique['id'].max() if 'id' in df_historique.columns else 0
    df_new['id'] = range(int(id_max) + 1, int(id_max) + 1 + len(df_new))

    # ── Traiter les valeurs manquantes ────────────────────────────────────
    print('\n🔧 Traitement des valeurs manquantes...')
    vars_numeriques = ['pm2_5_moyen', 'pm2_5_max', 'pm10_moyen', 'dust_moyen',
                       'co_moyen', 'no2_moyen', 'so2_moyen', 'ozone_moyen',
                       'uv_moyen', 'us_aqi_moyen']

    for col in vars_numeriques:
        if col in df_new.columns:
            nb_nan = df_new[col].isna().sum()
            if nb_nan > 0:
                for _, row in df_new[df_new[col].isna()].iterrows():
                    mediane = df_historique[
                        (df_historique['region'] == row['region']) &
                        (df_historique['date'].dt.month == date_ts.month)
                    ][col].median()
                    df_new.loc[df_new['ville'] == row['ville'], col] = mediane
                print(f'  {col:20s} : {nb_nan} manquants imputés')

    print('✅ Valeurs manquantes traitées')

    # ── Calculer les variables dérivées ───────────────────────────────────
    print('\n⚙️  Calcul des variables dérivées...')
    df_new_complet = calculer_variables_derivees(df_new, df_historique, AUJOURD_HUI)
    print('✅ Variables dérivées calculées')

    # ── Ajouter au dataset existant ───────────────────────────────────────
    df_updated = pd.concat([df_historique, df_new_complet], ignore_index=True)
    df_updated = df_updated.sort_values(['ville', 'date']).reset_index(drop=True)

    # ── Sauvegarder ───────────────────────────────────────────────────────
    print(f'\n💾 Sauvegarde dans {PATH_DATASET}...')
    #df_updated.to_excel(PATH_DATASET, index=False)
    df_updated.to_parquet(PATH_DATASET.replace('.xlsx', '.parquet'), index=False)
    print(f'✅ Dataset mis à jour : {len(df_updated):,} lignes')
    print(f'   Nouvelles lignes ajoutées : {len(df_new_complet)}')
    print(f'   Nouvelle période : {df_updated["date"].min().date()} → {df_updated["date"].max().date()}')
    
    
    print('\n' + '=' * 65)
    print('  ✅ Mise à jour terminée !')
    print('=' * 65)


if __name__ == '__main__':
    main()