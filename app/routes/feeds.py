from flask import Blueprint, redirect, render_template, request, url_for

from .. import db, fetcher, models

bp = Blueprint("feeds", __name__)


@bp.route("/feeds", methods=["GET", "POST"])
def index():
    conn = db.get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        feed_url = request.form.get("feed_url", "").strip()
        site_url = request.form.get("site_url", "").strip() or None
        category = request.form.get("category", "").strip() or None
        content_type = request.form.get("content_type", "article")
        if feed_url and not models.get_feed_by_url(conn, feed_url):
            feed_id = models.create_feed(
                conn,
                title=title or feed_url,
                feed_url=feed_url,
                site_url=site_url,
                category=category,
                content_type=content_type,
            )
            fetcher.fetch_single_feed_now(feed_id)
        return redirect(url_for("feeds.index"))

    feeds = models.list_feeds(conn, include_inactive=True)
    return render_template("feeds.html", feeds=feeds)


@bp.route("/feeds/<int:feed_id>/refresh", methods=["POST"])
def refresh(feed_id):
    fetcher.fetch_single_feed_now(feed_id)
    return redirect(url_for("feeds.index"))


@bp.route("/feeds/<int:feed_id>/toggle", methods=["POST"])
def toggle(feed_id):
    conn = db.get_db()
    feed = models.get_feed(conn, feed_id)
    if feed:
        models.set_feed_active(conn, feed_id, not feed["is_active"])
    return redirect(url_for("feeds.index"))


@bp.route("/feeds/<int:feed_id>", methods=["DELETE", "POST"])
def delete(feed_id):
    conn = db.get_db()
    models.set_feed_active(conn, feed_id, False)
    return redirect(url_for("feeds.index"))
