"""Accès à la base SQLite."""
import os
import sqlite3

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    titre         TEXT NOT NULL,
    description   TEXT NOT NULL,
    lieu          TEXT NOT NULL,
    priorite      TEXT NOT NULL DEFAULT 'moyenne',
    statut        TEXT NOT NULL DEFAULT 'nouveau',
    date_creation TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""


def get_db():
    """Une connexion par requête, stockée dans g."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Crée le dossier et la table au démarrage."""
    path = os.path.abspath(app.config["DATABASE_PATH"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    app.teardown_appcontext(close_db)
