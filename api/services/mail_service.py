# api/services/mail_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from api.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str):
        """Logic d'envoi basique via smtplib."""
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("[Mail] SMTP non configuré. L'email est affiché dans les logs au lieu d'être envoyé.")
            logger.info(f"[SIMULATED MAIL] To: {to_email} | Subject: {subject}\nContent: {html_content[:200]}...")
            return

        msg = MIMEMultipart()
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls() # Utilisation de TLS
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"[Mail] Email envoyé avec succès à {to_email}")
        except Exception as e:
            logger.error(f"[Mail] Échec de l'envoi de l'email : {str(e)}")

    @classmethod
    def send_air_quality_alert(cls, email: str, city: str, pm25: float, level: str, color: str):
        """Envoie un mail d'alerte PM2.5 stylisé."""
        subject = f"🚨 Alerte AirSentinel : Qualité de l'air {level} à {city}"
        
        html_template = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 15px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
                <div style="background: {color}; padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">AirSentinel Alerts</h1>
                </div>
                <div style="padding: 40px; text-align: center;">
                    <p style="text-transform: uppercase; letter-spacing: 2px; font-weight: 800; color: #94a3b8; font-size: 12px; margin-bottom: 10px;">Alerte de Qualité de l'Air</p>
                    <h2 style="font-size: 40px; margin: 0; color: white;">{pm25} <span style="font-size: 16px; opacity: 0.5;">µg/m³</span></h2>
                    <p style="color: #64748b; font-size: 14px; margin-top: 5px;">Concentration de PM2.5 à <strong>{city}</strong></p>
                    
                    <div style="margin: 30px 0; padding: 15px; border-radius: 10px; background: {color}22; border: 1px solid {color}44; color: {color}; font-weight: bold; text-transform: uppercase;">
                        Status: {level}
                    </div>
                    
                    <p style="color: #94a3b8; line-height: 1.6; font-size: 15px;">
                        Nous avons détecté une dégradation de la qualité de l'air dans votre région. 
                        Veuillez limiter vos activités de plein air et fermer vos fenêtres si possible.
                    </p>
                    
                    <a href="http://localhost:3000/dashboard/predictions" 
                       style="display: inline-block; margin-top: 30px; padding: 15px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 12px; font-weight: 900; text-transform: uppercase; font-size: 12px;">
                        Voir l'Analyse Complète
                    </a>
                </div>
                <div style="padding: 20px; background: #0f172a; text-align: center; font-size: 11px; color: #475569;">
                    &copy; 2026 AirSentinel Cameroon — Surveillance Intelligente. Tous droits réservés.
                </div>
            </div>
        </body>
        </html>
        """
        cls._send_email(email, subject, html_template)
