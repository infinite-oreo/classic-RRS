import os
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")
MIGRATIONS_DIR = os.path.join(BASE_DIR, "migrations")
LOG_DIR = os.path.join(DATA_DIR, "logs")
SECRET_KEY_PATH = os.path.join(DATA_DIR, "secret_key")

HOST = "127.0.0.1"
PORT = 5000


def _load_secret_key():
    """优先读取环境变量,其次复用本地持久化文件,都没有就随机生成并保存,
    避免像之前那样把签名密钥写死在代码里提交进版本库。"""
    env_key = os.environ.get("CLASSIC_RRS_SECRET_KEY")
    if env_key:
        return env_key
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(SECRET_KEY_PATH):
        with open(SECRET_KEY_PATH, "r", encoding="utf-8") as f:
            existing = f.read().strip()
        if existing:
            return existing
    new_key = secrets.token_hex(32)
    with open(SECRET_KEY_PATH, "w", encoding="utf-8") as f:
        f.write(new_key)
    return new_key


SECRET_KEY = _load_secret_key()

FETCH_INTERVAL_MINUTES = 15
FETCH_TIMEOUT_SECONDS = 12
FETCH_MAX_WORKERS = 6
FETCH_FAILURE_BACKOFF_THRESHOLD = 5
FETCH_MAX_BACKOFF_MINUTES = 24 * 60

# Supabase免费版项目连续7天无API活动会被自动暂停,这里每天ping一次_keepalive表防止暂停。
# anon key按Supabase的设计就是给客户端公开使用的,受RLS策略保护,写进代码库不是敏感信息泄露。
SUPABASE_URL = "https://vjqjphclshjgfpdufjlx.supabase.co"
SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZqcWpwaGNsc2hqZ2Zw"
    "ZHVmamx4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAxOTczNDgsImV4cCI6MjA5NTc3MzM0OH0.5YQ9hdE1gjs9OB"
    "rKA-N7OIAlwJm7WoHD8q-LQUywKbE"
)
SUPABASE_KEEPALIVE_INTERVAL_HOURS = 24
