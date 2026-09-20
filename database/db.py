import os
import sqlite3
from config import DATABASE_PATH


def get_connection():
    directory = os.path.dirname(DATABASE_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def _add_column(conn, table, column, definition):
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    conn = get_connection()
    conn.executescript("""
    BEGIN;
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT,
        language TEXT NOT NULL DEFAULT 'ar', is_banned INTEGER NOT NULL DEFAULT 0,
        referral_code TEXT UNIQUE, referred_by INTEGER, balance REAL NOT NULL DEFAULT 0 CHECK(balance >= 0),
        last_spin_at TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS wallet_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, type TEXT NOT NULL,
        amount REAL NOT NULL CHECK(amount >= 0), balance_before REAL NOT NULL CHECK(balance_before >= 0),
        balance_after REAL NOT NULL CHECK(balance_after >= 0), reference_id TEXT UNIQUE,
        admin_id INTEGER, description TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    CREATE TABLE IF NOT EXISTS wallet_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT NOT NULL UNIQUE, user_id INTEGER NOT NULL,
        kind TEXT NOT NULL CHECK(kind IN ('DEPOSIT','WITHDRAW')), amount REAL NOT NULL CHECK(amount > 0),
        method TEXT NOT NULL, account_details TEXT, payment_reference TEXT, status TEXT NOT NULL DEFAULT 'PENDING',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, decided_at TEXT, decided_by INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    CREATE TABLE IF NOT EXISTS lottery_rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, ticket_price REAL NOT NULL CHECK(ticket_price > 0),
        max_tickets INTEGER NOT NULL CHECK(max_tickets > 0), status TEXT NOT NULL, start_time TEXT,
        end_time TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS lottery_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT, round_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
        ticket_number INTEGER NOT NULL, price REAL NOT NULL CHECK(price > 0), is_winner INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(round_id) REFERENCES lottery_rounds(id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    CREATE TABLE IF NOT EXISTS gift_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE, amount REAL NOT NULL CHECK(amount > 0),
        usage_limit INTEGER NOT NULL CHECK(usage_limit > 0), used_count INTEGER NOT NULL DEFAULT 0,
        expires_at TEXT, is_active INTEGER NOT NULL DEFAULT 1, created_by INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS gift_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, code TEXT NOT NULL,
        amount REAL NOT NULL, used_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, code)
    );
    CREATE TABLE IF NOT EXISTS referral_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER NOT NULL, referred_user_id INTEGER NOT NULL UNIQUE,
        reward REAL NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS admin_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER NOT NULL,
        action TEXT NOT NULL, target_user_id INTEGER, details TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS support_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        message TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE INDEX IF NOT EXISTS idx_wallet_user ON wallet_transactions(user_id, created_at);
    CREATE INDEX IF NOT EXISTS idx_requests_status ON wallet_requests(status, kind);
    CREATE INDEX IF NOT EXISTS idx_tickets_round ON lottery_tickets(round_id);
    COMMIT;
    """)
    # Upgrade databases created by earlier revisions.
    _add_column(conn, "users", "last_spin_at", "TEXT")
    defaults = {
        "ticket_price": "10", "min_withdraw": "50", "max_withdraw": "5000",
        "referral_reward": "25", "welcome_bonus": "0", "wheel_cooldown_hours": "24",
        "maintenance_mode": "false", "deposit_methods": "ShamCash, MTN, Syriatel",
        "withdraw_methods": "ShamCash, MTN, Syriatel", "support_contact": "",
    }
    for key, value in defaults.items():
        conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (key, value))
    conn.close()


def ensure_user(user_id, username=None, first_name=None, last_name=None, language="ar"):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if row is None:
        code = f"LS{user_id % 1000000:06d}"
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT OR IGNORE INTO users(user_id,username,first_name,last_name,language,referral_code) VALUES(?,?,?,?,?,?)",
                     (user_id, username, first_name, last_name, language, code))
        conn.execute("COMMIT")
    else:
        conn.execute("UPDATE users SET username=?,first_name=?,last_name=?,last_seen=CURRENT_TIMESTAMP WHERE user_id=?",
                     (username, first_name, last_name, user_id))
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row)


def get_user(user_id):
    conn = get_connection(); row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone(); conn.close()
    return dict(row) if row else None


def set_user_language(user_id, language):
    conn = get_connection(); conn.execute("UPDATE users SET language=? WHERE user_id=?", (language, user_id)); conn.close()


def get_setting(key, default=""):
    conn = get_connection(); row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone(); conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_connection(); conn.execute("INSERT INTO settings(key,value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP", (key, str(value))); conn.close()


def log_admin_action(admin_id, action, target_user_id=None, details=""):
    conn = get_connection(); conn.execute("INSERT INTO admin_logs(admin_id,action,target_user_id,details) VALUES(?,?,?,?)", (admin_id, action, target_user_id, details)); conn.close()


def get_dashboard_stats():
    conn = get_connection()
    result = {
        "total_users": conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"],
        "active_users": conn.execute("SELECT COUNT(*) c FROM users WHERE last_seen >= datetime('now','-7 days')").fetchone()["c"],
        "total_balance": conn.execute("SELECT COALESCE(SUM(balance),0) c FROM users").fetchone()["c"],
        "total_deposits": conn.execute("SELECT COALESCE(SUM(amount),0) c FROM wallet_transactions WHERE type='DEPOSIT'").fetchone()["c"],
        "total_withdrawals": conn.execute("SELECT COALESCE(SUM(amount),0) c FROM wallet_transactions WHERE type='WITHDRAW'").fetchone()["c"],
        "total_tickets": conn.execute("SELECT COUNT(*) c FROM lottery_tickets").fetchone()["c"],
        "gift_usage": conn.execute("SELECT COUNT(*) c FROM gift_usage").fetchone()["c"],
        "referrals": conn.execute("SELECT COUNT(*) c FROM referral_records").fetchone()["c"],
    }
    conn.close(); return result


def ensure_default_round():
    conn = get_connection(); row = conn.execute("SELECT id FROM lottery_rounds WHERE status='ACTIVE' LIMIT 1").fetchone()
    if not row:
        conn.execute("INSERT INTO lottery_rounds(title,ticket_price,max_tickets,status,start_time,end_time) VALUES(?,?,?,'ACTIVE',CURRENT_TIMESTAMP,datetime('now','+7 days'))", ("Lucky Strike Round #1", float(get_setting("ticket_price", "10")), 500))
    conn.close()


if __name__ == "__main__":
    init_db(); ensure_default_round(); print("[OK] Database initialized")
