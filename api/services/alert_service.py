# api/services/alert_service.py

from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.models.user import User
from api.services.mail_service import EmailService
from api.routers.predictions import compute_interactive
from api.schemas.prediction import ComputeInput

logger = logging.getLogger(__name__)

class AlertService:
    @staticmethod
    async def process_alerts(db: AsyncSession):
        """
        Vérifie les PM2.5 pour chaque utilisateur abonné et envoie des mails si nécessaire.
        Logic simple : On utilise le même moteur de calcul que le simulateur interactif pour avoir le niveau actuel.
        En production, cela serait couplé à un flux de capteurs réels.
        """
        # 1. Récupérer tous les utilisateurs ayant une ville d'abonnement
        stmt = select(User).where(User.subscribed_city.isnot(None))
        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            logger.info("[AlertService] Aucun utilisateur abonné pour le moment.")
            return

        for user in users:
            try:
                # 2. Vérifier si on a déjà envoyé une alerte récemment (Cool down de 6 heures)
                if user.last_alert_sent and (datetime.now() - user.last_alert_sent) < timedelta(hours=6):
                    continue

                # 3. Calculer la qualité de l'air actuelle pour la ville (Simulation basée sur des features moyennes)
                # Note: On utilise des features par défaut 'moyennes' pour la détection
                features = {
                   "dust": 50, "co": 15, "uv": 5, "temp": 30, "humidity": 60, "ozone": 40
                }
                
                # Appeler la logique de prédiction pour cette ville
                prediction = compute_interactive(ComputeInput(city=user.subscribed_city, features=features))
                
                # 4. Si le niveau est critique (MAUVAIS ou TRÈS MAUVAIS), on alerte
                # MAUVAIS commence généralement au dessus de 55-100 selon les standards nationaux
                if prediction.level in ["MAUVAIS", "TRÈS MAUVAIS"]:
                    logger.info(f"[AlertService] Seuil franchi pour {user.email} à {user.subscribed_city} ({prediction.predicted_pm25} µg/m³)")
                    
                    # Envoi Mail
                    EmailService.send_air_quality_alert(
                        email=user.email,
                        city=user.subscribed_city,
                        pm25=prediction.predicted_pm25,
                        level=prediction.level,
                        color=prediction.color
                    )
                    
                    # Mise à jour du timestamp pour éviter le spam
                    user.last_alert_sent = datetime.now()
                    await db.commit()
            except Exception as e:
                logger.error(f"[AlertService] Erreur lors du traitement pour {user.email} : {str(e)}")
