import sqlite3
import os
from config import DATABASE_PATH


def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language TEXT DEFAULT 'ar',
            is_banned INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            referral_code TEXT,
            referred_by INTEGER,
            balance REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS wallet_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            balance_before REAL,
            balance_after REAL,
            reference_id TEXT,
            admin_id INTEGER,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS lottery_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            ticket_price REAL,
            max_tickets INTEGER,
            status TEXT,
            start_time TEXT,
            end_time TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS lottery_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_id INTEGER,
            user_id INTEGER,
            ticket_number INTEGER,
            price REAL,
            is_winner INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(round_id) REFERENCES lottery_rounds(id)
        );

        CREATE TABLE IF NOT EXISTS gift_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            amount REAL,
            usage_limit INTEGER,
            used_count INTEGER DEFAULT 0,
            expires_at TEXT,
            is_active INTEGER DEFAULT 1,
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS gift_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            code TEXT,
            amount REAL,
            used_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS referral_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_user_id INTEGER,
            reward REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            action TEXT,
            target_user_id INTEGER,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS support_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()

    # Set defaults
    conn = get_connection()
    default_settings = {
        "ticket_price": "10",
        "min_withdraw": "50",
        "max_withdraw": "5000",
        "referral_reward": "25",
        "welcome_bonus": "20",
        "wheel_cooldown_hours": "24",
        "maintenance_mode": "false",
        "deposit_methods": "ShamCash, MTN, Syriatel",
        "withdraw_methods": "ShamCash, MTN, Syriatel",
    }
    for key, value in default_settings.items():
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)",
            (key, value),
        )
    conn.commit()
    conn.close()


def ensure_user(user_id, username=None, first_name=None, last_name=None, language="ar"):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if user is None:
        referral_code = f"LS{user_id % 1000000:06d}"
        conn.execute(
            "INSERT INTO users(user_id, username, first_name, last_name, language, referral_code, balance) VALUES (?, ?, ?, ?, ?, ?, 0)",
            (user_id, username, first_name, last_name, language, referral_code),
        )
        conn.commit()
        conn.close()
        return get_user(user_id)
    conn.execute(
        "UPDATE users SET username = ?, first_name = ?, last_name = ?, last_seen = CURRENT_TIMESTAMP WHERE user_id = ?",
        (username, first_name, last_name, user_id),
    )
    conn.commit()
    conn.close()
    return get_user(user_id)


def get_user(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def set_user_language(user_id, language):
    conn = get_connection()
    conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
    conn.commit()
    conn.close()


def get_setting(key, default=""):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    if row is None:
        return default
    return row["value"]


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT INTO settings(key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP",
        (key, str(value)),
    )
    conn.commit()
    conn.close()


def record_transaction(user_id, tx_type, amount, balance_before, balance_after, reference_id=None, admin_id=None, description=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO wallet_transactions(user_id, type, amount, balance_before, balance_after, reference_id, admin_id, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, tx_type, amount, balance_before, balance_after, reference_id, admin_id, description),
    )
    conn.commit()
    conn.close()


def update_user_balance(user_id, new_balance):
    conn = get_connection()
    conn.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()
    conn.close()


def log_admin_action(admin_id, action, target_user_id=None, details=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO admin_logs(admin_id, action, target_user_id, details) VALUES (?, ?, ?, ?)",
        (admin_id, action, target_user_id, details),
    )
    conn.commit()
    conn.close()


def get_dashboard_stats():
    conn = get_connection()
    stats = {
        "total_users": conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"],
        "total_balance": conn.execute("SELECT COALESCE(SUM(balance),0) as c FROM users").fetchone()["c"],
        "total_deposits": conn.execute("SELECT COALESCE(SUM(amount),0) as c FROM wallet_transactions WHERE type='DEPOSIT'").fetchone()["c"],
        "total_withdrawals": conn.execute("SELECT COALESCE(SUM(amount),0) as c FROM wallet_transactions WHERE type='WITHDRAW'").fetchone()["c"],
        "total_tickets": conn.execute("SELECT COUNT(*) as c FROM lottery_tickets").fetchone()["c"],
        "gift_usage": conn.execute("SELECT COUNT(*) as c FROM gift_usage").fetchone()["c"],
        "referrals": conn.execute("SELECT COUNT(*) as c FROM referral_records").fetchone()["c"],
    }
    conn.close()
    return stats


def ensure_default_round():
    conn = get_connection()
    active = conn.execute("SELECT * FROM lottery_rounds WHERE status = 'ACTIVE' ORDER BY id DESC LIMIT 1").fetchone()
    if active is None:
        conn.execute(
            "INSERT INTO lottery_rounds(title, ticket_price, max_tickets, status, start_time, end_time) VALUES (?, ?, ?, 'ACTIVE', CURRENT_TIMESTAMP, datetime(CURRENT_TIMESTAMP, '+7 days'))",
            ("Lucky Strike Round #1", float(get_setting("ticket_price", "10")), 500),
        )
        conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    ensure_default_round()
    print("[OK] Database initialized")
