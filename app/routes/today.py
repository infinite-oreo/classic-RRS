import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from .. import db, models

bp = Blueprint("today", __name__)


@bp.route("/")
def index():
    return redirect(url_for("today.show"))


def _local_day_bounds(day=None):
    local_tz = datetime.datetime.now().astimezone().tzinfo
    if day is None:
        day = datetime.datetime.now(local_tz).date()
    start_local = datetime.datetime.combine(day, datetime.time.min, tzinfo=local_tz)
    end_local = start_local + datetime.timedelta(days=1)
    start_utc = start_local.astimezone(datetime.timezone.utc).isoformat()
    end_utc = end_local.astimezone(datetime.timezone.utc).isoformat()
    return start_utc, end_utc


@bp.route("/today")
def show():
    show_read = request.args.get("show_read") == "1"
    conn = db.get_db()
    start_utc, end_utc = _local_day_bounds()
    rows = models.entries_fetched_between(conn, start_utc, end_utc, show_read=show_read)
    groups = models.group_entries_by_feed(rows)
    groups.sort(
        key=lambda g: g["entries"][0]["published_at"] or "", reverse=True
    )
    return render_template("today.html", groups=groups, show_read=show_read)
