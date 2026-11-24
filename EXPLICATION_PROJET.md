# Explication complète du projet « gestion-incidents »

## 1. Vue d'ensemble
Une application Flask permet de gérer des incidents informatiques. Autour de l'application, une chaîne DevOps automatise tout le cycle :

```
Code -> Git/GitHub -> GitHub Actions (CI : tests, config Compose, build)
     -> CD : tests -> build -> publication dans GHCR (:latest et :sha)
     -> docker compose pull / up -d (compose.deploy.yaml) -> application en ligne
```

## 2. Les fichiers
| Fichier | Rôle |
|---|---|
| `app/__init__.py` | `create_app()` : crée l'application, déclare les routes, valide les formulaires |
| `app/db.py` | Connexion SQLite, création de la table `incidents` au démarrage |
| `app/templates/`, `app/static/style.css` | Interface HTML/CSS (page d'accueil en tableau de bord, liste filtrable, formulaire, détail). Thème clair/sombre automatique, responsive |
| `run.py` | Lancement en local (`python run.py`) |
| `tests/` | 8 tests pytest avec une base temporaire (la vraie base n'est jamais touchée) |
| `requirements.txt` | Dépendances : flask, gunicorn, pytest |
| `pytest.ini` | Indique à pytest où trouver le package `app` |
| `Dockerfile` | Recette de construction de l'image |
| `.dockerignore` / `.gitignore` | Fichiers exclus de l'image / de Git |
| `compose.yaml` | Démarrage en développement (construit l'image) |
| `compose.deploy.yaml` | Déploiement à partir de l'image publiée (aucun build) |
| `.github/workflows/ci.yml` | Intégration continue |
| `.github/workflows/cd.yml` | Publication dans GHCR |

### Routes
`/` accueil · `/incidents` liste (`?statut=`) · `/incidents/new` ajout · `/incidents/<id>` détail · `/incidents/<id>/statut` (POST) · `/incidents/<id>/delete` (POST) · `/health` · `/api/incidents`.

## 3. Dockerfile, ligne par ligne
- `FROM python:3.12-slim` : image de départ légère.
- `WORKDIR /app` : dossier de travail dans le conteneur.
- `COPY requirements.txt .` puis `RUN pip install` : les dépendances sont installées avant de copier le code, donc le cache Docker évite de tout réinstaller quand seul le code change.
- `COPY . .` : copie le code (en respectant `.dockerignore`).
- `ENV DATABASE_PATH=/data/incidents.db` : la base est dans `/data`, dossier destiné au volume.
- `useradd` / `USER appuser` : le conteneur ne tourne pas en root (sécurité).
- `EXPOSE 5000` : documente le port (le vrai mapping est fait par `ports:`).
- `CMD ["gunicorn", ...]` : serveur adapté à la production.

## 4. Compose
- `build: .` (dev) ou `image: ghcr.io/...` (déploiement).
- `ports: "5000:5000"` : port hôte : port conteneur.
- `restart: unless-stopped` : redémarre le conteneur sauf arrêt manuel.
- `volumes: incidents_data:/data` : volume nommé, les incidents survivent à `docker compose down` (mais pas à `down -v`).
- `healthcheck` : appelle `/health` pour savoir si l'application répond.

## 5. Workflows
**ci.yml** : se déclenche sur push et Pull Request vers `main`. Étapes : checkout, Python 3.12, installation, `pytest -v`, `docker compose config -q` (valide le YAML Compose), `docker compose build`. Si une étape échoue, les suivantes ne s'exécutent pas.

**cd.yml** : se déclenche sur push vers `main`.
- `permissions: packages: write` autorise la publication dans GHCR ; `contents: read` la lecture du dépôt.
- Job `test` puis job `publish` avec `needs: test` : pas d'image publiée si les tests échouent.
- L'étape `repo` met le nom du dépôt en minuscules (GHCR refuse les majuscules).
- `docker/login-action` s'authentifie avec `GITHUB_TOKEN` (aucun mot de passe personnel).
- `docker/build-push-action` construit et publie deux tags : `latest` (version courante) et `github.sha` (version exacte, permet un retour arrière).

## 6. Démonstration pas à pas
1. Mission 2 : `git init`, commits, branche `feature/gestion-incidents`, Pull Request, merge dans `main`.
2. Erreur volontaire : dans `/health`, remplacer `"OK"` par `"ERROR"` dans `app/__init__.py`, push, observer l'échec de l'étape *Executer les tests* dans l'onglet Actions (test `test_health`), corriger, push, pipeline vert. Capture avant/après.
3. Après le premier CD réussi : onglet Packages, vérifier les deux tags, rendre le package public.
4. `docker pull ghcr.io/<proprietaire>/gestion-incidents:latest` puis `docker images`.
5. `docker compose -f compose.deploy.yaml pull`, `up -d`, `logs`, tester dans le navigateur.
6. Mise à jour : changer `APP_VERSION` par défaut dans `app/__init__.py` (ex. `1.1.0`), push, attendre le pipeline, `pull`, `up -d`, la version affichée en pied de page change.

## 7. Réponses modèles aux questions de synthèse
(À reformuler avec vos propres mots : elles sont individuelles.)
1. **Git vs GitHub** : Git est l'outil local de gestion de versions ; GitHub est la plateforme en ligne qui héberge les dépôts Git et offre PR et Actions.
2. **Dockerfile** : fichier qui décrit pas à pas comment construire l'image de l'application.
3. **Image vs conteneur** : l'image est un modèle figé ; le conteneur est une instance en cours d'exécution de cette image.
4. **Docker Compose** : décrire et lancer une application (services, ports, volumes, variables) dans un fichier, avec une seule commande.
5. **Déclencheur du CI** : un push ou une Pull Request vers `main`.
6. **Tests avant publication** : éviter de publier une image défectueuse ; le job `publish` dépend de `test`.
7. **GHCR** : registre d'images de GitHub, qui stocke et distribue les images Docker.
8. **Tag SHA** : identifie précisément l'image issue d'un commit donné (traçabilité, retour arrière), alors que `latest` change à chaque publication.
9. **`docker build` vs `docker pull`** : `build` construit une image à partir d'un Dockerfile ; `pull` télécharge une image déjà construite depuis un registre.
10. **Déploiement automatique sur serveur distant** : serveur avec Docker, clé SSH dédiée, secrets GitHub (hôte, utilisateur, clé privée), environnements GitHub (test / production avec approbation), job de déploiement qui se connecte en SSH et exécute `docker compose pull && docker compose up -d`, puis vérifie `/health`.

## 8. Livrables et captures à faire
Dépôt GitHub complet (tous les fichiers ci-dessus) · capture pipeline CI réussi · capture échec puis correction · capture package GHCR avec les deux tags · capture application déployée · README · réponses aux 10 questions.
Barème : Git 2, appli et tests 2, Docker 2, Compose 2, CI 2, GHCR 2, déploiement 2, documentation et démo 6.
