import datetime
import xml.etree.ElementTree as ET

from . import models


def export_opml(conn):
    root = ET.Element("opml", version="2.0")
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = "classic RRS subscriptions"
    ET.SubElement(head, "dateCreated").text = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()
    body = ET.SubElement(root, "body")

    feeds = models.list_feeds(conn, include_inactive=True)
    category_nodes = {}
    for feed in feeds:
        category = feed["category"]
        parent = body
        if category:
            if category not in category_nodes:
                category_nodes[category] = ET.SubElement(body, "outline", text=category)
            parent = category_nodes[category]
        attrs = {
            "text": feed["title"] or feed["feed_url"],
            "title": feed["title"] or feed["feed_url"],
            "type": "rss",
            "xmlUrl": feed["feed_url"],
        }
        if feed["site_url"]:
            attrs["htmlUrl"] = feed["site_url"]
        ET.SubElement(parent, "outline", attrs)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _walk_outlines(outline_elements, category=None):
    result = []
    for outline in outline_elements:
        xml_url = outline.get("xmlUrl")
        if xml_url:
            result.append({
                "title": outline.get("title") or outline.get("text") or xml_url,
                "feed_url": xml_url,
                "site_url": outline.get("htmlUrl"),
                "category": category,
            })
        else:
            child_category = outline.get("text") or category
            result.extend(_walk_outlines(list(outline), category=child_category))
    return result


def parse_opml(file_bytes):
    root = ET.fromstring(file_bytes)
    body = root.find("body")
    if body is None:
        return []
    return _walk_outlines(list(body))


def import_opml(conn, file_bytes):
    entries = parse_opml(file_bytes)
    imported = 0
    skipped = 0
    for entry in entries:
        if models.get_feed_by_url(conn, entry["feed_url"]):
            skipped += 1
            continue
        models.create_feed(
            conn,
            title=entry["title"],
            feed_url=entry["feed_url"],
            site_url=entry["site_url"],
            category=entry["category"],
        )
        imported += 1
    return imported, skipped
