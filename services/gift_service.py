import random
from database.db import get_connection


def generate_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "LS-" + "".join(random.choice(chars) for _ in range(8))


def create_gift_code(amount, usage_limit, expires_at, created_by):
    code = generate_code()
    conn = get_connection()
    conn.execute(
        "INSERT INTO gift_codes(code, amount, usage_limit, used_count, expires_at, is_active, created_by) VALUES (?, ?, ?, 0, ?, 1, ?)",
        (code, amount, usage_limit, expires_at, created_by),
    )
    conn.commit()
    conn.close()
    return code


def redeem_gift_code(user_id, code):
    conn = get_connection()
    row = conn.execute("SELECT * FROM gift_codes WHERE code = ? AND is_active = 1", (code,)).fetchone()
    if not row:
        conn.close()
        return {"ok": False, "message": "Gift code not found or inactive"}
    if row["used_count"] >= row["usage_limit"]:
        conn.close()
        return {"ok": False, "message": "Gift code reached limit"}
    conn.execute("UPDATE gift_codes SET used_count = used_count + 1 WHERE id = ?", (row["id"],))
    conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (row["amount"], user_id))
    conn.execute("INSERT INTO gift_usage(user_id, code, amount) VALUES (?, ?, ?)", (user_id, code, row["amount"]))
    conn.execute("INSERT INTO wallet_transactions(user_id, type, amount, balance_before, balance_after, description) VALUES (?, 'GIFT', ?, ?, ?, ?)", (user_id, row["amount"], 0, row["amount"], "Gift code redemption"))
    conn.commit()
    conn.close()
    return {"ok": True, "amount": row["amount"]}
