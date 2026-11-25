"""Application Flask de gestion des incidents informatiques."""
import os

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

from .db import get_db, init_db

PRIORITES = {"faible": "Faible", "moyenne": "Moyenne", "elevee": "Élevée"}
STATUTS = {"nouveau": "Nouveau", "en_cours": "En cours", "resolu": "Résolu"}


def valider(form):
    """Retourne (données nettoyées, liste d'erreurs)."""
    data = {k: form.get(k, "").strip() for k in ("titre", "description", "lieu", "priorite")}
    erreurs = []
    if not data["titre"]:
        erreurs.append("Le titre est obligatoire.")
    if not data["description"]:
        erreurs.append("La description est obligatoire.")
    if not data["lieu"]:
        erreurs.append("Le lieu (salle ou laboratoire) est obligatoire.")
    if data["priorite"] not in PRIORITES:
        erreurs.append("La priorité doit être faible, moyenne ou élevée.")
    return data, erreurs


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE_PATH=os.environ.get("DATABASE_PATH", "data/incidents.db"),
        APP_VERSION=os.environ.get("APP_VERSION", "1.0.0"),
    )
    if config:
        app.config.update(config)
    init_db(app)

    @app.context_processor
    def inject():
        return {"PRIORITES": PRIORITES, "STATUTS": STATUTS, "version": app.config["APP_VERSION"]}

    def get_incident(incident_id):
        row = get_db().execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if row is None:
            abort(404)
        return row

    @app.route("/")
    def index():
        db = get_db()
        compte = {s: 0 for s in STATUTS}
        for r in db.execute("SELECT statut, COUNT(*) AS n FROM incidents GROUP BY statut"):
            compte[r["statut"]] = r["n"]
        recents = db.execute("SELECT * FROM incidents ORDER BY id DESC LIMIT 5").fetchall()
        return render_template("index.html", compte=compte, recents=recents)

    @app.route("/incidents")
    def liste():
        statut = request.args.get("statut", "")
        db = get_db()
        if statut in STATUTS:
            rows = db.execute("SELECT * FROM incidents WHERE statut = ? ORDER BY id DESC", (statut,)).fetchall()
        else:
            statut = ""
            rows = db.execute("SELECT * FROM incidents ORDER BY id DESC").fetchall()
        return render_template("list.html", incidents=rows, filtre=statut)

    @app.route("/incidents/new", methods=["GET", "POST"])
    def nouveau():
        if request.method == "POST":
            data, erreurs = valider(request.form)
            if erreurs:
                return render_template("new.html", erreurs=erreurs, valeurs=data), 400
            db = get_db()
            cur = db.execute(
                "INSERT INTO incidents (titre, description, lieu, priorite) VALUES (?, ?, ?, ?)",
                (data["titre"], data["description"], data["lieu"], data["priorite"]),
            )
            db.commit()
            flash("Incident ajouté.")
            return redirect(url_for("detail", incident_id=cur.lastrowid))
        return render_template("new.html", erreurs=[], valeurs={"priorite": "moyenne"})

    @app.route("/incidents/<int:incident_id>")
    def detail(incident_id):
        return render_template("detail.html", i=get_incident(incident_id))

    @app.route("/incidents/<int:incident_id>/statut", methods=["POST"])
    def changer_statut(incident_id):
        get_incident(incident_id)
        statut = request.form.get("statut", "")
        if statut not in STATUTS:
            abort(400)
        db = get_db()
        db.execute("UPDATE incidents SET statut = ? WHERE id = ?", (statut, incident_id))
        db.commit()
        flash("Statut mis à jour.")
        return redirect(url_for("detail", incident_id=incident_id))

    @app.route("/incidents/<int:incident_id>/delete", methods=["POST"])
    def supprimer(incident_id):
        get_incident(incident_id)
        db = get_db()
        db.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
        db.commit()
        flash("Incident supprimé.")
        return redirect(url_for("liste"))

    @app.route("/health")
    def health():
        return jsonify(status="ERROR")

    @app.route("/api/incidents")
    def api_incidents():
        rows = get_db().execute("SELECT * FROM incidents ORDER BY id DESC").fetchall()
        return jsonify([dict(r) for r in rows])

    return app
