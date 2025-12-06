FROM python:3.13.6-slim

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .
RUN touch /app/logs/django_errors.log


# Port exposé
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "core.wsgi", "--bind=0.0.0.0:8000"]