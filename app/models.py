import datetime


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ---------- feeds ----------

def list_feeds(conn, include_inactive=True):
    if include_inactive:
        rows = conn.execute("SELECT * FROM feeds ORDER BY title COLLATE NOCASE").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM feeds WHERE is_active = 1 ORDER BY title COLLATE NOCASE"
        ).fetchall()
    return rows


def get_feed(conn, feed_id):
    return conn.execute("SELECT * FROM feeds WHERE id = ?", (feed_id,)).fetchone()


def get_feed_by_url(conn, feed_url):
    return conn.execute("SELECT * FROM feeds WHERE feed_url = ?", (feed_url,)).fetchone()


def create_feed(conn, title, feed_url, site_url=None, category=None, content_type="article",
                 fetch_interval_minutes=60, is_active=1):
    cur = conn.execute(
        """
        INSERT INTO feeds (title, feed_url, site_url, category, content_type,
                            is_active, fetch_interval_minutes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (title, feed_url, site_url, category, content_type, is_active,
         fetch_interval_minutes, now_iso()),
    )
    conn.commit()
    return cur.lastrowid


def update_feed_title(conn, feed_id, title, category):
    conn.execute(
        "UPDATE feeds SET title = ?, category = ? WHERE id = ?", (title, category, feed_id)
    )
    conn.commit()


def set_feed_active(conn, feed_id, is_active):
    conn.execute("UPDATE feeds SET is_active = ? WHERE id = ?", (int(is_active), feed_id))
    conn.commit()


def record_fetch_success(conn, feed_id, etag, last_modified, fetch_interval_minutes):
    conn.execute(
        """
        UPDATE feeds
        SET last_fetched_at = ?, last_fetch_status = 'ok', last_fetch_error = NULL,
            consecutive_failures = 0, etag = ?, last_modified = ?, fetch_interval_minutes = ?
        WHERE id = ?
        """,
        (now_iso(), etag, last_modified, fetch_interval_minutes, feed_id),
    )
    conn.commit()


def record_fetch_failure(conn, feed_id, error_message, fetch_interval_minutes):
    conn.execute(
        """
        UPDATE feeds
        SET last_fetched_at = ?, last_fetch_status = 'error', last_fetch_error = ?,
            consecutive_failures = consecutive_failures + 1, fetch_interval_minutes = ?
        WHERE id = ?
        """,
        (now_iso(), error_message, fetch_interval_minutes, feed_id),
    )
    conn.commit()


def due_feeds(conn):
    rows = conn.execute("SELECT * FROM feeds WHERE is_active = 1").fetchall()
    due = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for row in rows:
        if not row["last_fetched_at"]:
            due.append(row)
            continue
        last = datetime.datetime.fromisoformat(row["last_fetched_at"])
        elapsed_minutes = (now - last).total_seconds() / 60
        if elapsed_minutes >= row["fetch_interval_minutes"]:
            due.append(row)
    return due


# ---------- entries ----------

def find_existing_entry(conn, feed_id, guid, link):
    if guid:
        row = conn.execute(
            "SELECT id FROM entries WHERE feed_id = ? AND guid = ?", (feed_id, guid)
        ).fetchone()
        if row:
            return row
    if link:
        row = conn.execute(
            "SELECT id FROM entries WHERE feed_id = ? AND link = ?", (feed_id, link)
        ).fetchone()
        if row:
            return row
    return None


def insert_entry(conn, feed_id, guid, link, title, author, summary, content_html,
                  published_at, enclosure_url, enclosure_type):
    cur = conn.execute(
        """
        INSERT INTO entries (feed_id, guid, link, title, author, summary, content_html,
                              published_at, fetched_at, enclosure_url, enclosure_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (feed_id, guid, link, title, author, summary, content_html,
         published_at, now_iso(), enclosure_url, enclosure_type),
    )
    conn.commit()
    return cur.lastrowid


def get_entry(conn, entry_id):
    return conn.execute(
        """
        SELECT entries.*, feeds.title AS feed_title, feeds.content_type AS feed_content_type
        FROM entries
        JOIN feeds ON feeds.id = entries.feed_id
        WHERE entries.id = ?
        """,
        (entry_id,),
    ).fetchone()


def set_entry_read(conn, entry_id, is_read):
    read_at = now_iso() if is_read else None
    conn.execute(
        "UPDATE entries SET is_read = ?, read_at = ? WHERE id = ?",
        (int(is_read), read_at, entry_id),
    )
    conn.commit()


def set_entry_favorited(conn, entry_id, is_favorited):
    conn.execute(
        "UPDATE entries SET is_favorited = ? WHERE id = ?", (int(is_favorited), entry_id)
    )
    conn.commit()


def entries_fetched_between(conn, start_iso, end_iso, show_read=False):
    query = """
        SELECT entries.*, feeds.title AS feed_title, feeds.content_type AS feed_content_type,
               feeds.category AS feed_category
        FROM entries
        JOIN feeds ON feeds.id = entries.feed_id
        WHERE entries.fetched_at >= ? AND entries.fetched_at < ?
    """
    params = [start_iso, end_iso]
    if not show_read:
        query += " AND entries.is_read = 0"
    query += " ORDER BY entries.published_at DESC"
    return conn.execute(query, params).fetchall()


def group_entries_by_feed(rows):
    groups = {}
    order = []
    for row in rows:
        feed_id = row["feed_id"]
        if feed_id not in groups:
            groups[feed_id] = {
                "feed_id": feed_id,
                "feed_title": row["feed_title"],
                "feed_content_type": row["feed_content_type"],
                "feed_category": row["feed_category"],
                "entries": [],
            }
            order.append(feed_id)
        groups[feed_id]["entries"].append(row)
    return [groups[fid] for fid in order]


def list_favorites(conn):
    return conn.execute(
        """
        SELECT entries.*, feeds.title AS feed_title, feeds.content_type AS feed_content_type
        FROM entries
        JOIN feeds ON feeds.id = entries.feed_id
        WHERE entries.is_favorited = 1
        ORDER BY entries.published_at DESC
        """
    ).fetchall()
