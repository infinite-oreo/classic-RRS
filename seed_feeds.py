"""一次性把 AI / 编程比赛相关的 RSS 源灌进订阅列表。

跑法: python seed_feeds.py
重复运行是安全的,已存在的 feed_url 会被跳过。
"""
import logging

from app import config, db, fetcher, models

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

FEEDS = [
    # (标题, RSS地址, 分类, 说明用的site_url)
    ("MLH (Major League Hacking)", "https://news.mlh.io/feed", "Hackathon", "https://mlh.io"),
    ("Dev.to · hackathon 标签", "https://dev.to/feed/tag/hackathon", "Hackathon", "https://dev.to/t/hackathon"),
    ("HN 搜索 · hackathon", "https://hnrss.org/newest?q=hackathon", "Hackathon", "https://hn.algolia.com/?q=hackathon"),
    ("HN 搜索 · AI hackathon", 'https://hnrss.org/newest?q=%22AI+hackathon%22', "Hackathon", "https://hn.algolia.com/?q=AI%20hackathon"),
    ("Dev.to · ai 标签", "https://dev.to/feed/tag/ai", "AI比赛", "https://dev.to/t/ai"),
    ("Dev.to · machinelearning 标签", "https://dev.to/feed/tag/machinelearning", "AI比赛", "https://dev.to/t/machinelearning"),
    ("Dev.to · llm 标签", "https://dev.to/feed/tag/llm", "AI比赛", "https://dev.to/t/llm"),
    ("HN 搜索 · Kaggle", "https://hnrss.org/newest?q=Kaggle", "AI比赛", "https://hn.algolia.com/?q=Kaggle"),
    ("Dev.to · competition 标签", "https://dev.to/feed/tag/competition", "编程比赛", "https://dev.to/t/competition"),
    ("HN 搜索 · CTF", "https://hnrss.org/newest?q=CTF", "编程比赛", "https://hn.algolia.com/?q=CTF"),
]


def main():
    db.init_db()
    new_feed_ids = []
    conn = db.get_connection()
    try:
        for title, feed_url, category, site_url in FEEDS:
            if models.get_feed_by_url(conn, feed_url):
                logging.info("已存在,跳过: %s", title)
                continue
            feed_id = models.create_feed(
                conn, title=title, feed_url=feed_url, site_url=site_url, category=category,
            )
            new_feed_ids.append(feed_id)
            logging.info("已添加: %s -> feed_id=%s", title, feed_id)
    finally:
        conn.close()

    if new_feed_ids:
        logging.info("开始拉取一次新添加的订阅源...")
        for feed_id in new_feed_ids:
            fetcher.fetch_single_feed_now(feed_id)
    logging.info("完成,访问 http://%s:%s/today 查看", config.HOST, config.PORT)


if __name__ == "__main__":
    main()
