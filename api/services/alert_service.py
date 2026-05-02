# api/services/alert_service.py

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.models.user import User
from api.services.mail_service import EmailService

logger = logging.getLogger(__name__)


class AlertService:
    @staticmethod
    async def process_alerts(db: AsyncSession):
        """
        Vérifie les PM2.5 pour chaque utilisateur abonné et envoie des notifications si nécessaire.
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
                # 2. Cool-down de 6 heures pour éviter le spam
                if user.last_alert_sent and (datetime.now(timezone.utc) - user.last_alert_sent) < timedelta(hours=6):
                    logger.debug(f"[AlertService] Cool-down actif pour {user.email}, skip.")
                    continue

                # 3. Calcul de la qualité de l'air (simulation via features moyennes)
                features = {
                    "dust": 50.0, "co": 15.0, "uv": 5.0,
                    "temp": 30.0, "humidity": 60.0, "ozone": 40.0
                }

                prediction = compute_interactive(ComputeInput(city=user.subscribed_city, features=features))

                # 4. Alerte uniquement si niveau MAUVAIS ou TRÈS MAUVAIS
                if prediction.level in ["MAUVAIS", "TRÈS MAUVAIS"]:
                    logger.info(
                        f"[AlertService] Seuil franchi pour {user.email} "
                        f"à {user.subscribed_city} ({prediction.predicted_pm25} µg/m³)"
                    )

                    # Envoi Email (synchrone, non bloquant car dans un executor possible)
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

            except Exception as e:
                logger.error(f"[AlertService] Erreur lors du traitement pour {user.email} : {str(e)}")
