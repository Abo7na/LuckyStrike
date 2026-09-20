import shutil
from datetime import datetime
from pathlib import Path
from config import DATABASE_PATH, BACKUP_DIR


def create_database_backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    target = BACKUP_DIR / f"luckystrike_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DATABASE_PATH, target)
    return target
