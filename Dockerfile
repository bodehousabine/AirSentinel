FROM python:3.11-slim

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires pour certaines bibliothèques (ex: lightgbm, xgboost)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des bibliothèques Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie de tout le code du projet dans le conteneur
COPY . .

# Hugging Face Spaces utilise le port 7860 par défaut
ENV PORT=7860
EXPOSE 7860

# Commande de lancement (pointe vers votre api/main.py)
CMD ["python", "api/main.py"]
