import calendar
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor

import bleach
import feedparser
import socket

from . import config, models

logger = logging.getLogger(__name__)

ALLOWED_TAGS = list(bleach.ALLOWED_TAGS) + [
    "p", "br", "img", "h1", "h2", "h3", "h4", "pre", "span", "div", "figure", "figcaption",
]
ALLOWED_ATTRS = {
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title"],
}


def _clean_html(raw):
    if not raw:
        return raw
    return bleach.clean(raw, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)


def _struct_time_to_iso(struct_time):
    if not struct_time:
        return None
    timestamp = calendar.timegm(struct_time)
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc).isoformat()


def _extract_enclosure(entry):
    for link in entry.get("links", []):
        if link.get("rel") == "enclosure" and link.get("href"):
            return link.get("href"), link.get("type")
    return None, None


def fetch_feed(conn, feed_row):
    feed_id = feed_row["id"]
    socket.setdefaulttimeout(config.FETCH_TIMEOUT_SECONDS)
    try:
        parsed = feedparser.parse(
            feed_row["feed_url"],
            etag=feed_row["etag"] or None,
            modified=feed_row["last_modified"] or None,
        )
    except Exception as exc:  # network-level failures feedparser doesn't catch itself
        _handle_failure(conn, feed_row, str(exc))
        return

    status = getattr(parsed, "status", None)
    if status == 304:
        models.record_fetch_success(
            conn, feed_id, feed_row["etag"], feed_row["last_modified"],
            feed_row["fetch_interval_minutes"],
        )
        return

    if status is not None and status >= 400:
        _handle_failure(conn, feed_row, f"HTTP {status}")
        return

    if parsed.bozo and not parsed.entries:
        _handle_failure(conn, feed_row, str(parsed.get("bozo_exception", "解析失败")))
        return

    for entry in parsed.entries:
        guid = entry.get("id") or entry.get("guid")
        link = entry.get("link")
        existing = models.find_existing_entry(conn, feed_id, guid, link)
        if existing:
            continue

        published_at = _struct_time_to_iso(
            entry.get("published_parsed") or entry.get("updated_parsed")
        )
        summary = _clean_html(entry.get("summary"))
        content_html = None
        if entry.get("content"):
            content_html = _clean_html(entry["content"][0].get("value"))
        enclosure_url, enclosure_type = _extract_enclosure(entry)

        models.insert_entry(
            conn, feed_id, guid, link,
            entry.get("title"), entry.get("author"),
            summary, content_html, published_at,
            enclosure_url, enclosure_type,
        )

    new_interval = feed_row["fetch_interval_minutes"]
    models.record_fetch_success(
        conn, feed_id,
        parsed.get("etag"), parsed.get("modified"),
        new_interval,
    )


def _handle_failure(conn, feed_row, error_message):
    failures = feed_row["consecutive_failures"] + 1
    interval = feed_row["fetch_interval_minutes"]
    if failures >= config.FETCH_FAILURE_BACKOFF_THRESHOLD:
        interval = min(interval * 2, config.FETCH_MAX_BACKOFF_MINUTES)
    models.record_fetch_failure(conn, feed_row["id"], error_message[:500], interval)
    logger.warning("抓取失败 feed_id=%s url=%s error=%s", feed_row["id"], feed_row["feed_url"], error_message)


def _fetch_one(feed_id):
    from . import db
    conn = db.get_connection()
    try:
        feed_row = models.get_feed(conn, feed_id)
        if feed_row:
            fetch_feed(conn, feed_row)
    finally:
        conn.close()


def run_fetch_cycle():
    from . import db
    conn = db.get_connection()
    try:
        due = models.due_feeds(conn)
        feed_ids = [row["id"] for row in due]
    finally:
        conn.close()

    if not feed_ids:
        return

    with ThreadPoolExecutor(max_workers=config.FETCH_MAX_WORKERS) as executor:
        executor.map(_fetch_one, feed_ids)


def fetch_single_feed_now(feed_id):
    _fetch_one(feed_id)
