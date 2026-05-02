# api/services/notification_service.py

import firebase_admin
from firebase_admin import credentials, messaging
import os
import logging

logger = logging.getLogger(__name__)

# Initialisation de Firebase
try:
    cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase-service-account.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info("[Firebase] SDK initialisé avec succès.")
    else:
        logger.warning("[Firebase] Fichier de clé non trouvé. Les notifications seront simulées.")
except Exception as e:
    logger.error(f"[Firebase] Erreur d'initialisation : {e}")

class NotificationService:
    @staticmethod
    def send_push_notification(token: str, title: str, body: str, data: dict = None):
        """
        Envoie une notification push via Firebase Cloud Messaging.
        """
        if not token:
            return

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )

        try:
            response = messaging.send(message)
            logger.info(f"[Firebase] Notification envoyée avec succès : {response}")
            return response
        except Exception as e:
            logger.error(f"[Firebase] Échec de l'envoi de la notification : {e}")
            return None

    @classmethod
    def send_air_quality_alert(cls, token: str, city: str, pm25: float, level: str):
        """
        Envoie une alerte spécifique à la qualité de l'air.
        """
        title = f"🚨 Alerte Qualité de l'Air : {level}"
        body = f"La concentration de PM2.5 à {city} est de {pm25} µg/m³. Prenez vos précautions."
        
        return cls.send_push_notification(
            token=token,
            title=title,
            body=body,
            data={
                "city": city,
                "pm25": str(pm25),
                "level": level,
                "type": "air_quality_alert"
            }
        )
