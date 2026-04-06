# api/migrate.py

import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def migrate():
    if not DATABASE_URL:
        print("❌ Erreur : DATABASE_URL non trouvée dans .env")
        return

    print(f"🔄 Connexion à la base de données...")
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        print("🔨 Ajout des colonnes manquantes à la table 'users'...")
        
        # SQL pour ajouter les colonnes si elles n'existent pas
        sql_commands = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscribed_city VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_alert_sent TIMESTAMP WITH TIME ZONE;"
        ]
        
        for sql in sql_commands:
            try:
                await conn.execute(text(sql))
                print(f"✅ Executé : {sql}")
            except Exception as e:
                print(f"⚠️ Erreur lors de l'exécution de '{sql}': {e}")

    await engine.dispose()
    print("🚀 Migration terminée avec succès !")

if __name__ == "__main__":
    asyncio.run(migrate())
