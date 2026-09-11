CREATE TABLE IF NOT EXISTS feeds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    feed_url TEXT NOT NULL UNIQUE,
    site_url TEXT,
    category TEXT,
    content_type TEXT NOT NULL DEFAULT 'article',
    is_active INTEGER NOT NULL DEFAULT 1,
    fetch_interval_minutes INTEGER NOT NULL DEFAULT 60,
    last_fetched_at TEXT,
    last_fetch_status TEXT,
    last_fetch_error TEXT,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    etag TEXT,
    last_modified TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feed_id INTEGER NOT NULL REFERENCES feeds(id) ON DELETE CASCADE,
    guid TEXT,
    link TEXT,
    title TEXT,
    author TEXT,
    summary TEXT,
    content_html TEXT,
    published_at TEXT,
    fetched_at TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    is_favorited INTEGER NOT NULL DEFAULT 0,
    read_at TEXT,
    enclosure_url TEXT,
    enclosure_type TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_feed_id ON entries(feed_id);
CREATE INDEX IF NOT EXISTS idx_entries_fetched_at ON entries(fetched_at);
CREATE INDEX IF NOT EXISTS idx_entries_published_at ON entries(published_at);
CREATE INDEX IF NOT EXISTS idx_entries_feed_guid ON entries(feed_id, guid);
CREATE INDEX IF NOT EXISTS idx_entries_feed_link ON entries(feed_id, link);
