# Utilisez une image de base Python
FROM python:3.8-slim

# Définissez le répertoire de travail
WORKDIR /app

# Copiez les fichiers nécessaires dans le conteneur
COPY requirements.txt .
COPY main.py .
COPY templates/ templates/
COPY logstash/pipeline logstash/pipeline/

# Installez les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Commande pour lancer votre application Flask
CMD ["python3", "main.py"]