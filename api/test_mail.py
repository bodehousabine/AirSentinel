import sys
import os
from pathlib import Path

# Ajouter la racine du projet au path pour importer api
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from api.services.mail_service import EmailService
from api.core.config import settings

def test_alert():
    print(f"--- Test d'envoi d'email ---")
    print(f"SMTP Host: {settings.SMTP_HOST}")
    print(f"SMTP User: {settings.SMTP_USER}")
    
    if "VOTRE_EMAIL" in settings.SMTP_USER:
        print("ERROR: Vous devez d'abord remplacer 'VOTRE_EMAIL@gmail.com' par votre vraie adresse dans le fichier api/.env")
        return

    test_email = settings.SMTP_USER # On s'envoie le mail à soi-même pour tester
    
    try:
        EmailService.send_air_quality_alert(
            email=test_email,
            city="Douala (Test)",
            pm25=45.5,
            level="MAUVAIS",
            color="#FF5722"
        )
        print(f"SUCCESS ! Un email de test a été envoyé à {test_email}")
        print("Veuillez vérifier votre boîte de réception (et vos spams).")
    except Exception as e:
        print(f"FAILURE : {e}")

if __name__ == "__main__":
    test_alert()
