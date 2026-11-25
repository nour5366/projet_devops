# Gestion des incidents informatiques

Application web (Flask + SQLite) pour signaler et suivre les incidents dans les salles et laboratoires d'un établissement, avec une chaîne DevOps complète : Git/GitHub, Docker, Docker Compose, GitHub Actions (CI/CD) et GHCR.

**Auteurs :** Nour Mahfoudh et [nom du binôme] (DSI3, module DevOps 2026-2027)

**Dépôt :** https://github.com/nour5366/projet_devops

## Fonctionnalités
Ajouter, lister (avec filtre par statut), consulter, changer le statut et supprimer un incident. Route `/health` et API `/api/incidents`.

## Structure
```
app/ (code + templates + CSS)   tests/ (8 tests pytest)
Dockerfile  compose.yaml  compose.deploy.yaml
.github/workflows/ci.yml  cd.yml
```

## Lancer en local
```bash
python -m venv venv && source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
python run.py            # http://localhost:5000
pytest -v                # tests
```

## Avec Docker seul (Mission 3)
```bash
docker build -t gestion-incidents .
docker run -d --name gestion-incidents -p 5000:5000 gestion-incidents
docker ps                      # vérifier le conteneur
docker logs gestion-incidents  # journaux
# puis ouvrir http://localhost:5000
docker stop gestion-incidents && docker rm gestion-incidents
```

## Avec Docker Compose (développement)
```bash
docker compose up -d --build
docker compose ps
docker compose logs
docker compose down
```

## Pipeline
```
git push / PR -> GitHub Actions -> tests -> docker compose config -q -> docker compose build
git push main -> tests -> build -> login GHCR (GITHUB_TOKEN) -> push :latest et :<sha>
```
- `ci.yml` : push et Pull Request vers `main`.
- `cd.yml` : push vers `main`, le job `publish` dépend du job `test`.

## Déploiement depuis GHCR
L'image publiée est `ghcr.io/nour5366/gestion-incidents` (tags `latest` et `<sha du commit>`).
1. Après le premier CD réussi, rendre le package public (GitHub > Packages > Package settings > Change visibility) ou faire `docker login ghcr.io` avec un jeton autorisé (ne jamais partager ce jeton).
2. Récupérer et lancer :
```bash
docker pull ghcr.io/nour5366/gestion-incidents:latest
docker images
docker compose -f compose.deploy.yaml pull
docker compose -f compose.deploy.yaml up -d
docker compose -f compose.deploy.yaml ps
docker compose -f compose.deploy.yaml logs
docker compose -f compose.deploy.yaml down
```

## Mettre à jour l'application
Changer la valeur par défaut de `APP_VERSION` dans `app/__init__.py` (ex. `1.1.0`), `git push` sur `main`, attendre le pipeline (CI + CD), puis `docker compose -f compose.deploy.yaml pull` et `up -d`. La version affichée en pied de page change.

## Captures d'écran
Le dossier `captures/` contient : pipeline CI réussi, échec volontaire puis correction, workflow CD, package GHCR (tags), application déployée.
