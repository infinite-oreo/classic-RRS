import logging
import urllib.request

from . import config

logger = logging.getLogger(__name__)


def ping():
    """对Supabase的_keepalive表做一次轻量SELECT,防止免费版项目因7天无活动被自动暂停。"""
    url = f"{config.SUPABASE_URL}/rest/v1/_keepalive?select=id&limit=1"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": config.SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {config.SUPABASE_ANON_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
        logger.info("Supabase keepalive ping 成功")
    except Exception as exc:
        logger.warning("Supabase keepalive ping 失败: %s", exc)
