"""
=============================================================================
 AirSentinel Cameroun — Équipe DPA Green Tech
=============================================================================
 SCRIPT : backfill_missing.py
 Télécharge les données manquantes : 21 déc 2025 → 31 mars 2026

 UTILISATION :
   python backfill_missing.py

 Durée estimée : ~40 minutes (101 jours × 2 sec entre villes)
=============================================================================
"""

import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import numpy as np
import time
import os
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

PATH_DATASET = 'data/processed/dataset_final.xlsx'
PATH_PARQUET = 'data/processed/dataset_final.parquet'

DATE_DEBUT = datetime(2025, 12, 21)  # ← date minimale disponible
DATE_FIN   = datetime(2026, 3, 31)

URL_METEO = 'https://archive-api.open-meteo.com/v1/archive'
URL_POLL  = 'https://air-quality-api.open-meteo.com/v1/air-quality'

VARS_METEO = [
    'weather_code', 'temperature_2m_max', 'temperature_2m_min',
    'temperature_2m_mean', 'apparent_temperature_max', 'apparent_temperature_min',
    'apparent_temperature_mean', 'sunrise', 'sunset', 'daylight_duration',
    'sunshine_duration', 'precipitation_sum', 'rain_sum', 'snowfall_sum',
    'precipitation_hours', 'wind_speed_10m_max', 'wind_gusts_10m_max',
    'wind_direction_10m_dominant', 'shortwave_radiation_sum',
    'et0_fao_evapotranspiration',
]

VARS_POLL = [
    'pm2_5', 'pm10', 'nitrogen_dioxide', 'sulphur_dioxide', 'ozone',
    'carbon_monoxide', 'dust', 'uv_index', 'us_aqi',
    'us_aqi_pm2_5', 'us_aqi_pm10', 'us_aqi_nitrogen_dioxide',
    'us_aqi_ozone', 'us_aqi_sulphur_dioxide', 'us_aqi_carbon_monoxide',
]

# Seuils PM2.5 OMS AQG 2021
SEUIL_AQG = 15.0
SEUIL_IT4 = 25.0
SEUIL_IT3 = 37.5
SEUIL_IT2 = 50.0
SEUIL_IT1 = 75.0

# Temps d'attente réduit — données historiques
TEMPS_ATTENTE = 10

VILLES_CAMEROUN = [
    {'ville': 'Meiganga',    'region': 'Adamaoua',     'latitude': 6.5167,  'longitude': 14.3000},
    {'ville': 'Ngaoundere',  'region': 'Adamaoua',     'latitude': 7.3167,  'longitude': 13.5833},
    {'ville': 'Tibati',      'region': 'Adamaoua',     'latitude': 6.4667,  'longitude': 12.6333},
    {'ville': 'Tignere',     'region': 'Adamaoua',     'latitude': 7.3667,  'longitude': 12.6500},
    {'ville': 'Akonolinga',  'region': 'Centre',       'latitude': 3.7667,  'longitude': 12.2500},
    {'ville': 'Bafia',       'region': 'Centre',       'latitude': 4.7500,  'longitude': 11.2333},
    {'ville': 'Mbalmayo',    'region': 'Centre',       'latitude': 3.5167,  'longitude': 11.5000},
    {'ville': 'Yaounde',     'region': 'Centre',       'latitude': 3.8667,  'longitude': 11.5167},
    {'ville': 'Abong-Mbang', 'region': 'Est',          'latitude': 3.9833,  'longitude': 13.1667},
    {'ville': 'Batouri',     'region': 'Est',          'latitude': 4.4333,  'longitude': 14.3667},
    {'ville': 'Bertoua',     'region': 'Est',          'latitude': 4.5833,  'longitude': 13.6833},
    {'ville': 'Yokadouma',   'region': 'Est',          'latitude': 3.5167,  'longitude': 15.0500},
    {'ville': 'Kousseri',    'region': 'Extreme-Nord', 'latitude': 12.0833, 'longitude': 15.0333},
    {'ville': 'Maroua',      'region': 'Extreme-Nord', 'latitude': 10.5833, 'longitude': 14.3167},
    {'ville': 'Mokolo',      'region': 'Extreme-Nord', 'latitude': 10.7333, 'longitude': 13.8000},
    {'ville': 'Yagoua',      'region': 'Extreme-Nord', 'latitude': 10.3333, 'longitude': 15.2333},
    {'ville': 'Douala',      'region': 'Littoral',     'latitude': 4.0483,  'longitude': 9.7000},
    {'ville': 'Edea',        'region': 'Littoral',     'latitude': 3.8000,  'longitude': 10.1333},
    {'ville': 'Loum',        'region': 'Littoral',     'latitude': 4.7167,  'longitude': 9.7333},
    {'ville': 'Nkongsamba',  'region': 'Littoral',     'latitude': 4.9500,  'longitude': 9.9333},
    {'ville': 'Garoua',      'region': 'Nord',         'latitude': 9.3000,  'longitude': 13.3833},
    {'ville': 'Guider',      'region': 'Nord',         'latitude': 9.9333,  'longitude': 13.9500},
    {'ville': 'Poli',        'region': 'Nord',         'latitude': 8.4833,  'longitude': 13.2333},
    {'ville': 'Touboro',     'region': 'Nord',         'latitude': 7.7667,  'longitude': 15.3667},
    {'ville': 'Bamenda',     'region': 'Nord-Ouest',   'latitude': 5.9500,  'longitude': 10.1500},
    {'ville': 'Kumbo',       'region': 'Nord-Ouest',   'latitude': 6.2000,  'longitude': 10.6833},
    {'ville': 'Mbengwi',     'region': 'Nord-Ouest',   'latitude': 6.0167,  'longitude': 10.0000},
    {'ville': 'Wum',         'region': 'Nord-Ouest',   'latitude': 6.3833,  'longitude': 10.0667},
    {'ville': 'Bafoussam',   'region': 'Ouest',        'latitude': 5.4667,  'longitude': 10.4167},
    {'ville': 'Dschang',     'region': 'Ouest',        'latitude': 5.4500,  'longitude': 10.0500},
    {'ville': 'Foumban',     'region': 'Ouest',        'latitude': 5.7167,  'longitude': 10.9000},
    {'ville': 'Mbouda',      'region': 'Ouest',        'latitude': 5.6333,  'longitude': 10.2500},
    {'ville': 'Ambam',       'region': 'Sud',          'latitude': 2.3833,  'longitude': 11.2833},
    {'ville': 'Ebolowa',     'region': 'Sud',          'latitude': 2.9000,  'longitude': 11.1500},
    {'ville': 'Kribi',       'region': 'Sud',          'latitude': 2.9500,  'longitude': 9.9167},
    {'ville': 'Sangmelima',  'region': 'Sud',          'latitude': 2.9333,  'longitude': 11.9833},
    {'ville': 'Buea',        'region': 'Sud-Ouest',    'latitude': 4.1500,  'longitude': 9.2333},
    {'ville': 'Kumba',       'region': 'Sud-Ouest',    'latitude': 4.6333,  'longitude': 9.4500},
    {'ville': 'Limbe',       'region': 'Sud-Ouest',    'latitude': 4.0167,  'longitude': 9.2000},
    {'ville': 'Mamfe',       'region': 'Sud-Ouest',    'latitude': 5.7667,  'longitude': 9.3000},
]

# ─────────────────────────────────────────────────────────────────────────────
# CLIENT OPEN-METEO
# ─────────────────────────────────────────────────────────────────────────────

cache_session    = requests_cache.CachedSession('.cache_backfill', expire_after=-1)
retry_session    = retry(cache_session, retries=5, backoff_factor=0.5)
openmeteo_client = openmeteo_requests.Client(session=retry_session)

# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS DE TÉLÉCHARGEMENT
# ─────────────────────────────────────────────────────────────────────────────

def telecharger_meteo_ville(ville_info, date_str):
    try:
        params = {
            'latitude':   ville_info['latitude'],
            'longitude':  ville_info['longitude'],
            'daily':      VARS_METEO,
            'start_date': date_str,
            'end_date':   date_str,
            'timezone':   'Africa/Douala',
        }
        reponses   = openmeteo_client.weather_api(URL_METEO, params=params)
        daily      = reponses[0].Daily()
        daily_data = {
            'date':      pd.to_datetime(date_str),
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
        print(f'ERREUR: {e}')
        return None


def telecharger_pollution_ville(ville_info, date_str):
    try:
        params = {
            'latitude':   ville_info['latitude'],
            'longitude':  ville_info['longitude'],
            'hourly':     VARS_POLL,
            'start_date': date_str,
            'end_date':   date_str,
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
        aqi_dict = {
            'PM2.5': df_h['aqi_pm25'].mean(),
            'PM10':  df_h['aqi_pm10'].mean(),
            'NO2':   df_h['aqi_no2'].mean(),
            'Ozone': df_h['aqi_ozone'].mean(),
            'SO2':   df_h['aqi_so2'].mean(),
            'CO':    df_h['aqi_co'].mean(),
        }
        row_poll['polluant_dominant'] = max(aqi_dict, key=aqi_dict.get)
        aqi = row_poll['us_aqi_moyen']
        if   aqi <= 50:  row_poll['niveau_alerte'] = 'BON'
        elif aqi <= 100: row_poll['niveau_alerte'] = 'MODÉRÉ'
        elif aqi <= 150: row_poll['niveau_alerte'] = 'MAUVAIS SENSIBLES'
        elif aqi <= 200: row_poll['niveau_alerte'] = 'MAUVAIS'
        elif aqi <= 300: row_poll['niveau_alerte'] = 'TRÈS MAUVAIS'
        else:            row_poll['niveau_alerte'] = 'DANGEREUX'
        return row_poll
    except Exception as e:
        print(f'ERREUR: {e}')
        return None


def calculer_variables_derivees(df_new, df_historique, date_str):
    date_ts = pd.Timestamp(date_str)
    df_new['annee']      = df_new['date'].dt.year
    df_new['mois']       = df_new['date'].dt.month
    df_new['jour_annee'] = df_new['date'].dt.dayofyear
    df_new['saison_code'] = df_new['mois'].apply(
        lambda m: 0 if m in [11, 12, 1, 2, 3] else 1)
    df_new['pm2_5_log'] = np.log1p(df_new['pm2_5_moyen'])

    df_combined = pd.concat([df_historique, df_new], ignore_index=True)
    df_combined = df_combined.sort_values(['ville', 'date']).reset_index(drop=True)

    df_combined['pm2_5_lag_1j']  = df_combined.groupby('ville')['pm2_5_moyen'].shift(1)
    df_combined['pm2_5_lag_3j']  = df_combined.groupby('ville')['pm2_5_moyen'].shift(3)
    df_combined['pm2_5_lag_7j']  = df_combined.groupby('ville')['pm2_5_moyen'].shift(7)
    df_combined['pm2_5_moy_7j']  = df_combined.groupby('ville')['pm2_5_moyen'].transform(
        lambda x: x.shift(1).rolling(7, min_periods=1).mean())
    df_combined['pm2_5_moy_30j'] = df_combined.groupby('ville')['pm2_5_moyen'].transform(
        lambda x: x.shift(1).rolling(30, min_periods=1).mean())

    df_combined['indice_stagnation'] = (
        (df_combined['wind_speed_10m_max'] < df_combined['wind_speed_10m_max'].quantile(0.25)).astype(int) +
        (df_combined['precipitation_sum']  < 1.0).astype(int)
    )

    seuil_dust  = df_combined.groupby('region')['dust_moyen'].transform(lambda x: x.quantile(0.90))
    seuil_pluie = df_combined.groupby('region')['precipitation_sum'].transform(lambda x: x.quantile(0.10))
    df_combined['harmattan_intense'] = (
        (df_combined['dust_moyen']        > seuil_dust) &
        (df_combined['precipitation_sum'] < seuil_pluie)
    ).astype(int)

    seuil_co = df_combined[df_combined['saison_code'] == 0]['co_moyen'].quantile(0.90)
    df_combined['episode_feux'] = (
        (df_combined['co_moyen']    > seuil_co) &
        (df_combined['saison_code'] == 0)
    ).astype(int)

    regions = ['Adamaoua', 'Centre', 'Est', 'Extreme-Nord',
               'Littoral', 'Nord', 'Nord-Ouest', 'Ouest', 'Sud', 'Sud-Ouest']
    for reg in regions:
        df_combined[f'region_{reg}'] = (df_combined['region'] == reg).astype(int)

    def calculer_irs(pm25):
        if   pm25 <= SEUIL_AQG: return 0
        elif pm25 <= SEUIL_IT4: return 1
        elif pm25 <= SEUIL_IT3: return 2
        elif pm25 <= SEUIL_IT2: return 3
        elif pm25 <= SEUIL_IT1: return 4
        else:                   return 5

    def niveau_sanitaire(irs):
        return {0:'FAIBLE',1:'MODÉRÉ',2:'ÉLEVÉ',
                3:'TRÈS ÉLEVÉ',4:'CRITIQUE',5:'DANGEREUX'}.get(irs, 'N/A')

    df_combined['IRS_brut']         = df_combined['pm2_5_moyen'].apply(calculer_irs)
    df_combined['IRS']              = df_combined['IRS_brut']
    df_combined['niveau_sanitaire'] = df_combined['IRS_brut'].apply(niveau_sanitaire)

    return df_combined[df_combined['date'] == date_ts].copy()


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAMME PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print('=' * 65)
    print('  AirSentinel — Backfill données manquantes')
    print(f'  Période : {DATE_DEBUT.date()} → {DATE_FIN.date()}')
    print('=' * 65)

    # Charger dataset existant
    print(f'\n📂 Chargement de {PATH_DATASET}...')
    df_historique = pd.read_excel(PATH_DATASET)
    df_historique['date'] = pd.to_datetime(df_historique['date'])
    print(f'✅ Dataset chargé : {len(df_historique):,} lignes')
    print(f'   Période actuelle : {df_historique["date"].min().date()} → {df_historique["date"].max().date()}')

    # Dates déjà présentes
    dates_presentes = set(df_historique['date'].dt.date)

    # Générer la liste des dates manquantes
    dates_manquantes = []
    date_courante = DATE_DEBUT
    while date_courante <= DATE_FIN:
        if date_courante.date() not in dates_presentes:
            dates_manquantes.append(date_courante)
        date_courante += timedelta(days=1)

    print(f'\n📅 Dates manquantes : {len(dates_manquantes)} jours')
    if not dates_manquantes:
        print('✅ Aucune donnée manquante — base déjà complète !')
        return

    print(f'   De {dates_manquantes[0].date()} à {dates_manquantes[-1].date()}')
    duree_min = len(dates_manquantes) * len(VILLES_CAMEROUN) * TEMPS_ATTENTE / 60
    print(f'   Durée estimée : ~{duree_min:.0f} minutes')
    print()

    # Télécharger jour par jour
    for i_jour, date_obj in enumerate(dates_manquantes, 1):
        date_str = date_obj.strftime('%Y-%m-%d')
        print(f'\n📅 [{i_jour:03d}/{len(dates_manquantes)}] {date_str}')

        nouvelles_lignes = []
        succes = 0

        for ville_info in VILLES_CAMEROUN:
            nom = ville_info['ville']
            print(f'  {nom}...', end=' ', flush=True)

            row_meteo = telecharger_meteo_ville(ville_info, date_str)
            if row_meteo is None:
                print('❌')
                continue

            row_poll = telecharger_pollution_ville(ville_info, date_str)
            if row_poll is None:
                print('❌')
                continue

            row = {**row_meteo, **row_poll}
            nouvelles_lignes.append(row)
            succes += 1
            print(f'✅ {row["pm2_5_moyen"]:.1f}', end=' ')

            time.sleep(TEMPS_ATTENTE)

        print(f'\n  → {succes}/40 villes téléchargées')

        if not nouvelles_lignes:
            print(f'  ⚠️ Aucune donnée pour {date_str} — on passe')
            continue

        # Créer DataFrame du jour
        df_new = pd.DataFrame(nouvelles_lignes)
        df_new['date'] = pd.to_datetime(df_new['date'])

        # Ajouter id
        id_max = df_historique['id'].max() if 'id' in df_historique.columns else 0
        df_new['id'] = range(int(id_max) + 1, int(id_max) + 1 + len(df_new))

        # Traiter valeurs manquantes
        vars_num = ['pm2_5_moyen', 'pm2_5_max', 'pm10_moyen', 'dust_moyen',
                    'co_moyen', 'no2_moyen', 'so2_moyen', 'ozone_moyen',
                    'uv_moyen', 'us_aqi_moyen']
        for col in vars_num:
            if col in df_new.columns:
                nb_nan = df_new[col].isna().sum()
                if nb_nan > 0:
                    for _, row in df_new[df_new[col].isna()].iterrows():
                        mediane = df_historique[
                            (df_historique['region'] == row['region']) &
                            (df_historique['date'].dt.month == date_obj.month)
                        ][col].median()
                        df_new.loc[df_new['ville'] == row['ville'], col] = mediane

        # Calculer variables dérivées
        df_new_complet = calculer_variables_derivees(df_new, df_historique, date_str)

        # Ajouter à l'historique
        df_historique = pd.concat([df_historique, df_new_complet], ignore_index=True)
        df_historique = df_historique.sort_values(['ville', 'date']).reset_index(drop=True)

        # Sauvegarder toutes les 10 jours
        if i_jour % 10 == 0 or i_jour == len(dates_manquantes):
            print(f'  💾 Sauvegarde... ({len(df_historique):,} lignes)', end=' ')
            df_historique.to_excel(PATH_DATASET, index=False)
            df_historique.to_parquet(PATH_PARQUET, index=False)
            print('✅')

    # Sauvegarde finale
    print(f'\n💾 Sauvegarde finale...')
    df_historique.to_excel(PATH_DATASET, index=False)
    df_historique.to_parquet(PATH_PARQUET, index=False)

    print(f'\n✅ Dataset mis à jour : {len(df_historique):,} lignes')
    print(f'   Période : {df_historique["date"].min().date()} → {df_historique["date"].max().date()}')
    print('\n🎉 Backfill terminé !')


if __name__ == '__main__':
    main()
