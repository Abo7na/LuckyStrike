from pathlib import Path
from config import DATABASE_PATH, BACKUP_DIR


def create_database_backup():
    source = Path(DATABASE_PATH)
    if not source.exists():
        raise FileNotFoundError("Database does not exist yet")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    target = BACKUP_DIR / f"luckystrike_backup_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    # SQLite WAL may contain recent committed pages; use SQLite's online backup API.
    import sqlite3
    source_conn = sqlite3.connect(source)
    target_conn = sqlite3.connect(target)
    try:
        source_conn.backup(target_conn)
    finally:
        target_conn.close()
        source_conn.close()
    return target
