import secrets
from datetime import datetime, timezone
from database.db import get_connection


def generate_code():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "LS-" + "".join(secrets.choice(alphabet) for _ in range(10))


def create_gift_code(amount, usage_limit, expires_at, created_by):
    if float(amount) <= 0 or int(usage_limit) <= 0:
        raise ValueError("amount and usage_limit must be positive")
    for _ in range(5):
        code = generate_code()
        conn = get_connection()
        try:
            conn.execute("INSERT INTO gift_codes(code,amount,usage_limit,expires_at,created_by) VALUES(?,?,?,?,?)", (code, float(amount), int(usage_limit), expires_at, created_by))
            return code
        except Exception:
            continue
        finally:
            conn.close()
    raise RuntimeError("Could not generate a unique gift code")


def redeem_gift_code(user_id, raw_code):
    code = raw_code.strip().upper()
    conn = get_connection(); conn.execute("BEGIN IMMEDIATE")
    try:
        user = conn.execute("SELECT balance,is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
        row = conn.execute("SELECT * FROM gift_codes WHERE code=? AND is_active=1", (code,)).fetchone()
        if not user or user["is_banned"]:
            conn.execute("ROLLBACK"); return {"ok": False, "message": "User unavailable"}
        if not row:
            conn.execute("ROLLBACK"); return {"ok": False, "message": "Gift code not found or inactive"}
        if conn.execute("SELECT 1 FROM gift_usage WHERE user_id=? AND code=?", (user_id, code)).fetchone():
            conn.execute("ROLLBACK"); return {"ok": False, "message": "Code already used by this account"}
        if row["expires_at"]:
            expiry = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
            if expiry.tzinfo is None: expiry = expiry.replace(tzinfo=timezone.utc)
            if expiry <= datetime.now(timezone.utc):
                conn.execute("ROLLBACK"); return {"ok": False, "message": "Gift code expired"}
        if row["used_count"] >= row["usage_limit"]:
            conn.execute("ROLLBACK"); return {"ok": False, "message": "Gift code reached its usage limit"}
        amount = float(row["amount"]); before = float(user["balance"]); after = before + amount
        ref = f"gift_{row['id']}_{user_id}"
        conn.execute("UPDATE gift_codes SET used_count=used_count+1 WHERE id=? AND used_count<usage_limit", (row["id"],))
        if conn.execute("SELECT changes()").fetchone()[0] != 1:
            conn.execute("ROLLBACK"); return {"ok": False, "message": "Gift code reached its usage limit"}
        conn.execute("UPDATE users SET balance=? WHERE user_id=?", (after, user_id))
        conn.execute("INSERT INTO gift_usage(user_id,code,amount) VALUES(?,?,?)", (user_id, code, amount))
        conn.execute("INSERT INTO wallet_transactions(user_id,type,amount,balance_before,balance_after,reference_id,description) VALUES(?,?,?,?,?,?,?)", (user_id, "GIFT", amount, before, after, ref, "Gift code redemption"))
        conn.execute("COMMIT"); return {"ok": True, "amount": amount, "balance": after}
    except Exception:
        conn.execute("ROLLBACK"); raise
    finally:
        conn.close()
