# Gestion des incidents informatiques

Application web (Flask + SQLite) pour signaler et suivre les incidents dans les salles et laboratoires d'un établissement, avec une chaîne DevOps complète : Git/GitHub, Docker, Docker Compose, GitHub Actions (CI/CD) et GHCR.

**Auteurs :** Étudiant A, Étudiant B (DSI3, module DevOps 2026-2027)

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
1. Dans `compose.deploy.yaml`, remplacer `REMPLACER_PROPRIETAIRE` par votre nom GitHub (minuscules).
2. Rendre le package public (GitHub > Packages > Package settings > Change visibility).
```bash
docker compose -f compose.deploy.yaml pull
docker compose -f compose.deploy.yaml up -d
docker compose -f compose.deploy.yaml logs
docker compose -f compose.deploy.yaml down
```

## Mettre à jour l'application
Changer `APP_VERSION` ou un texte, `git push` sur `main`, attendre le pipeline, puis `pull` et `up -d` avec `compose.deploy.yaml`.
