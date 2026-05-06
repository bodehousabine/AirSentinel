# api/services/alert_service.py

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.models.user import User
from api.services.mail_service import EmailService

logger = logging.getLogger(__name__)

# Features moyennes réalistes par ville (basées sur les données IndabaX Cameroun)
# Reflètent les conditions typiques qui produisent des alertes pour les villes polluées
CITY_FEATURES = {
    "douala":       {"dust": 55.0, "co": 25.0, "uv": 6.0, "temp": 29.0, "humidity": 80.0, "ozone": 45.0},
    "yaoundé":      {"dust": 40.0, "co": 18.0, "uv": 5.5, "temp": 24.0, "humidity": 75.0, "ozone": 40.0},
    "yaounde":      {"dust": 40.0, "co": 18.0, "uv": 5.5, "temp": 24.0, "humidity": 75.0, "ozone": 40.0},
    "garoua":       {"dust": 90.0, "co": 20.0, "uv": 8.0, "temp": 38.0, "humidity": 30.0, "ozone": 55.0},
    "maroua":       {"dust": 110.0, "co": 22.0, "uv": 9.0, "temp": 40.0, "humidity": 20.0, "ozone": 60.0},
    "ngaoundéré":   {"dust": 60.0, "co": 15.0, "uv": 7.0, "temp": 22.0, "humidity": 65.0, "ozone": 50.0},
    "ngaoundere":   {"dust": 60.0, "co": 15.0, "uv": 7.0, "temp": 22.0, "humidity": 65.0, "ozone": 50.0},
    "bafoussam":    {"dust": 35.0, "co": 12.0, "uv": 5.0, "temp": 20.0, "humidity": 70.0, "ozone": 38.0},
    "bamenda":      {"dust": 38.0, "co": 13.0, "uv": 5.0, "temp": 22.0, "humidity": 72.0, "ozone": 38.0},
    "bertoua":      {"dust": 50.0, "co": 14.0, "uv": 6.0, "temp": 26.0, "humidity": 78.0, "ozone": 42.0},
    "kribi":        {"dust": 20.0, "co": 8.0,  "uv": 7.0, "temp": 27.0, "humidity": 85.0, "ozone": 30.0},
    "ebolowa":      {"dust": 25.0, "co": 9.0,  "uv": 5.5, "temp": 25.0, "humidity": 80.0, "ozone": 32.0},
    "touboro":      {"dust": 75.0, "co": 18.0, "uv": 8.5, "temp": 36.0, "humidity": 35.0, "ozone": 52.0},
    "buéa":         {"dust": 18.0, "co": 7.0,  "uv": 5.0, "temp": 22.0, "humidity": 88.0, "ozone": 28.0},
    "buea":         {"dust": 18.0, "co": 7.0,  "uv": 5.0, "temp": 22.0, "humidity": 88.0, "ozone": 28.0},
}
# Features par défaut pour les villes non listées
DEFAULT_FEATURES = {"dust": 50.0, "co": 15.0, "uv": 6.0, "temp": 30.0, "humidity": 60.0, "ozone": 42.0}


class AlertService:
    @staticmethod
    async def process_alerts(db: AsyncSession):
        """
        Vérifie les PM2.5 pour chaque utilisateur abonné et envoie des notifications si nécessaire.
        Utilise des features réalistes par ville pour produire des prédictions pertinentes.
        """
        # 1. Récupérer les utilisateurs abonnés avec alertes actives
        stmt = select(User).where(
            User.subscribed_city.isnot(None),
            User.subscribed_city != "",
            User.is_alerts_enabled == True
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            logger.info("[AlertService] Aucun utilisateur abonné pour le moment.")
            return

        # Import ici pour éviter un import circulaire au niveau du module
        from api.routers.predictions import compute_interactive
        from api.schemas.prediction import ComputeInput

        for user in users:
            try:
                # 2. Cool-down de 3 heures pour éviter le spam
                if user.last_alert_sent and (datetime.now(timezone.utc) - user.last_alert_sent) < timedelta(hours=3):
                    logger.debug(f"[AlertService] Cool-down actif pour {user.email}, skip.")
                    continue

                # 3. Features réalistes selon la ville de l'utilisateur
                city_key = user.subscribed_city.lower().strip()
                features = CITY_FEATURES.get(city_key, DEFAULT_FEATURES)
                logger.info(f"[AlertService] Calcul pour {user.email} @ {user.subscribed_city} (features city-specific)")

                prediction = compute_interactive(ComputeInput(city=user.subscribed_city, features=features))
                logger.info(
                    f"[AlertService] Niveau prédit : {prediction.level} "
                    f"({prediction.predicted_pm25} µg/m³) pour {user.subscribed_city}"
                )

                # 4. Alerte si PM2.5 > 15 µg/m³ (aligné sur les recommandations de l'OMS 2021)
                if prediction.predicted_pm25 > 15:
                    logger.info(
                        f"[AlertService] Seuil franchi pour {user.email} "
                        f"à {user.subscribed_city} ({prediction.predicted_pm25} µg/m³)"
                    )

                    # Envoi Email
                    try:
                        EmailService.send_air_quality_alert(
                            email=user.email,
                            city=user.subscribed_city,
                            pm25=prediction.predicted_pm25,
                            level=prediction.level,
                            color=prediction.color,
                        )
                    except Exception as mail_err:
                        logger.error(f"[AlertService] Erreur mail pour {user.email}: {mail_err}")

                    # Envoi Push Notification (FCM)
                    if user.fcm_token:
                        try:
                            from api.services.notification_service import NotificationService
                            await NotificationService.send_air_quality_alert(
                                token=user.fcm_token,
                                city=user.subscribed_city,
                                pm25=prediction.predicted_pm25,
                                level=prediction.level,
                            )
                        except Exception as push_err:
                            logger.error(f"[AlertService] Erreur push pour {user.email}: {push_err}")

                    # Mise à jour du timestamp pour éviter le spam
                    user.last_alert_sent = datetime.now(timezone.utc)
                    await db.commit()

                else:
                    logger.info(
                        f"[AlertService] Niveau {prediction.level} pour {user.subscribed_city} — "
                        f"pas d'alerte nécessaire."
                    )

            except Exception as e:
                logger.error(f"[AlertService] Erreur lors du traitement pour {user.email} : {str(e)}")
