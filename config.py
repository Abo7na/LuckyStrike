import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "luckystrike.db"))
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
APP_NAME = "Lucky Strike"
LOG_DIR = BASE_DIR / "logs"
BACKUP_DIR = BASE_DIR / "backups"

if not BOT_TOKEN:
    print("[WARN] BOT_TOKEN is not set. Add it to .env before running the bot.")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(Path(DATABASE_PATH).parent, exist_ok=True)
