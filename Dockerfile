# 1. Image de base légère
FROM python:3.12-slim
# 2. Répertoire de travail
WORKDIR /app
# 3. Dépendances d'abord (cache de couches Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 4. Code de l'application
COPY . .
# 5. Dossier des données + utilisateur non-root
ENV DATABASE_PATH=/data/incidents.db
RUN useradd -m appuser && mkdir /data && chown appuser /data
USER appuser
# 6. Port documenté et commande de démarrage
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
