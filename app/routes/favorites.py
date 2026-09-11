from flask import Blueprint, render_template

from .. import db, models

bp = Blueprint("favorites", __name__)


@bp.route("/favorites")
def index():
    conn = db.get_db()
    entries = models.list_favorites(conn)
    return render_template("favorites.html", entries=entries)
