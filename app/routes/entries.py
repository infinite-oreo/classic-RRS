from flask import Blueprint, abort, render_template, request

from .. import db, models

bp = Blueprint("entries", __name__)


@bp.route("/entries/<int:entry_id>")
def detail(entry_id):
    conn = db.get_db()
    entry = models.get_entry(conn, entry_id)
    if not entry:
        abort(404)
    return render_template("entry_detail.html", entry=entry)


@bp.route("/entries/<int:entry_id>/read", methods=["POST"])
def mark_read(entry_id):
    conn = db.get_db()
    entry = models.get_entry(conn, entry_id)
    if not entry:
        abort(404)
    models.set_entry_read(conn, entry_id, not entry["is_read"])
    entry = models.get_entry(conn, entry_id)
    if request.headers.get("HX-Request"):
        return render_template("_entry_row.html", entry=entry)
    return ("", 204)


@bp.route("/entries/<int:entry_id>/favorite", methods=["POST"])
def mark_favorite(entry_id):
    conn = db.get_db()
    entry = models.get_entry(conn, entry_id)
    if not entry:
        abort(404)
    models.set_entry_favorited(conn, entry_id, not entry["is_favorited"])
    entry = models.get_entry(conn, entry_id)
    if request.headers.get("HX-Request"):
        return render_template("_entry_row.html", entry=entry)
    return ("", 204)
