import datetime

from flask import Blueprint, render_template, request

from .. import db, models
from .today import _local_day_bounds

bp = Blueprint("archive", __name__)


@bp.route("/archive")
def show():
    date_str = request.args.get("date")
    if date_str:
        try:
            day = datetime.date.fromisoformat(date_str)
        except ValueError:
            day = datetime.date.today()
    else:
        day = datetime.date.today()

    conn = db.get_db()
    start_utc, end_utc = _local_day_bounds(day)
    rows = models.entries_fetched_between(conn, start_utc, end_utc, show_read=True)
    groups = models.group_entries_by_feed(rows)
    groups.sort(
        key=lambda g: g["entries"][0]["published_at"] or "", reverse=True
    )
    return render_template("archive.html", groups=groups, day=day)
