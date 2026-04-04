import pandas as pd
from pathlib import Path
from api.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

# Variable globale pour stocker le DataFrame en mémoire (Singleton)
_df = None

def get_dataframe() -> pd.DataFrame:
    """
    Charge le dataset CSV en mémoire une seule fois et retourne le DataFrame.
    Gère le cas où le fichier n'existe pas.
    """
    global _df
    if _df is not None:
        return _df
        
    settings = get_settings()
    # On part de la racine du projet pour s'assurer que 'data/' est toujours trouvé
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / settings.DATASET_PATH
    
    if not dataset_path.exists():
        logger.error(f"Fichier introuvable: {dataset_path}")
        raise FileNotFoundError(f"Le fichier de données '{dataset_path}' n'existe pas.")
        
    try:
        # TODO: Ajuster le paramètre `parse_dates=['date']` si le nom de la colonne temporel diffère
        _df = pd.read_csv(dataset_path, parse_dates=['date'])
        
        # ─── VIRTUAL TIME SHIFT (Live Demo Mode) ───
        # Pour que l'app paraisse "Live", on décale les dates pour que le dataset finisse AUJOURD'HUI.
        if 'date' in _df.columns:
            max_date = _df['date'].max()
            today = pd.Timestamp.now().normalize()
            if not pd.isna(max_date):
                delta = today - max_date
                _df['date'] = _df['date'] + delta
                logger.info(f"Dataset décalé de {delta.days} jours pour correspondre à la date actuelle ({today.date()})")
        
        logger.info(f"Dataset chargé avec succès depuis {dataset_path}")
    except ValueError:
        # Si la colonne 'date' n'existe pas, on tente un chargement normal 
        _df = pd.read_csv(dataset_path)
        logger.warning("Dataset chargé, mais aucune colonne 'date' n'a pu être parsée. (À vérifier)")
    
    return _df

def apply_filters(df: pd.DataFrame, villes=None, regions=None, annee_min=2020, annee_max=2025) -> pd.DataFrame:
    """
    Applique des filtres géographiques et temporels sur le DataFrame.
    
    TODO: Ajuster les noms des colonnes 'city' et 'region' selon ce qui se trouve dans le CSV final.
    """
    filtered_df = df.copy()
    
    if villes:
        # Filtrer par ville(s)
        filtered_df = filtered_df[filtered_df['city'].isin(villes)]
        
    if regions:
        # Filtrer par région(s)
        filtered_df = filtered_df[filtered_df['region'].isin(regions)]
        
    # Filtrer par date (année) si la colonne date est bien présente et au format datetime
    if 'date' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.year >= annee_min) & 
            (filtered_df['date'].dt.year <= annee_max)
        ]
        
    return filtered_df
