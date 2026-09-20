import uuid
from database.db import get_connection, get_setting


def get_balance(user_id):
    conn = get_connection()
    row = conn.execute("SELECT balance FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return float(row["balance"]) if row else 0.0


def _change_balance(conn, user_id, amount, tx_type, reference_id, description, admin_id=None):
    row = conn.execute("SELECT balance,is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
    if not row or row["is_banned"]:
        return {"ok": False, "message": "User unavailable"}
    before = float(row["balance"])
    after = before + float(amount)
    if after < 0:
        return {"ok": False, "message": "Insufficient balance"}
    conn.execute("UPDATE users SET balance=? WHERE user_id=?", (after, user_id))
    conn.execute("INSERT INTO wallet_transactions(user_id,type,amount,balance_before,balance_after,reference_id,admin_id,description) VALUES(?,?,?,?,?,?,?,?)",
                 (user_id, tx_type, abs(float(amount)), before, after, reference_id, admin_id, description))
    return {"ok": True, "balance": after}


def apply_balance_change(user_id, amount, tx_type, reference_id=None, description="", admin_id=None):
    reference_id = reference_id or str(uuid.uuid4())
    conn = get_connection()
    conn.execute("BEGIN IMMEDIATE")
    try:
        if conn.execute("SELECT 1 FROM wallet_transactions WHERE reference_id=?", (reference_id,)).fetchone():
            conn.execute("ROLLBACK")
            return {"ok": True, "duplicate": True}
        result = _change_balance(conn, user_id, amount, tx_type, reference_id, description, admin_id)
        if not result["ok"]:
            conn.execute("ROLLBACK")
            return result
        conn.execute("COMMIT")
        return result
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def add_balance(user_id, amount, reference_id=None, description="ADMIN", admin_id=None):
    result = apply_balance_change(user_id, abs(float(amount)), "DEPOSIT", reference_id, description, admin_id)
    return result.get("balance") if result.get("ok") else None


def deduct_balance(user_id, amount, reference_id=None, description="SYSTEM", admin_id=None):
    result = apply_balance_change(user_id, -abs(float(amount)), "GAME", reference_id, description, admin_id)
    return result.get("ok", False)


def create_deposit_request(user_id, amount, method, payment_reference):
    amount = float(amount)
    if amount <= 0 or not method.strip() or not payment_reference.strip():
        return {"ok": False, "message": "Invalid deposit data"}
    request_id = "dep_" + uuid.uuid4().hex
    conn = get_connection()
    try:
        conn.execute("INSERT INTO wallet_requests(request_id,user_id,kind,amount,method,payment_reference) VALUES(?,?, 'DEPOSIT',?,?,?)",
                     (request_id, user_id, amount, method.strip(), payment_reference.strip()))
        return {"ok": True, "request_id": request_id}
    finally:
        conn.close()


def request_withdrawal(user_id, amount, method, account_details):
    amount = float(amount)
    request_id = "wd_" + uuid.uuid4().hex
    conn = get_connection()
    conn.execute("BEGIN IMMEDIATE")
    try:
        if amount < float(get_setting("min_withdraw", "50")) or amount > float(get_setting("max_withdraw", "5000")):
            conn.execute("ROLLBACK")
            return {"ok": False, "message": "Withdrawal amount is outside limits"}
        result = _change_balance(conn, user_id, -amount, "WITHDRAW_HOLD", request_id, f"{method}:{account_details}")
        if not result["ok"]:
            conn.execute("ROLLBACK")
            return result
        conn.execute("INSERT INTO wallet_requests(request_id,user_id,kind,amount,method,account_details) VALUES(?,?, 'WITHDRAW',?,?,?)",
                     (request_id, user_id, amount, method.strip(), account_details.strip()))
        conn.execute("COMMIT")
        return {"ok": True, "request_id": request_id}
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def decide_request(request_id, admin_id, approve, reason=""):
    conn = get_connection()
    conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute("SELECT * FROM wallet_requests WHERE request_id=? AND status='PENDING'", (request_id,)).fetchone()
        if not row:
            conn.execute("ROLLBACK")
            return {"ok": False, "message": "Request already processed or missing"}
        status = "APPROVED" if approve else "REJECTED"
        if not approve and row["kind"] == "WITHDRAW":
            result = _change_balance(conn, row["user_id"], row["amount"], "REFUND", "refund_" + request_id, reason or "Withdrawal rejected", admin_id)
            if not result["ok"]:
                conn.execute("ROLLBACK")
                return result
        if approve and row["kind"] == "DEPOSIT":
            result = _change_balance(conn, row["user_id"], row["amount"], "DEPOSIT", request_id, reason or "Deposit approved", admin_id)
            if not result["ok"]:
                conn.execute("ROLLBACK")
                return result
        conn.execute("UPDATE wallet_requests SET status=?,decided_at=CURRENT_TIMESTAMP,decided_by=? WHERE request_id=?",
                     (status, admin_id, request_id))
        conn.execute("COMMIT")
        return {"ok": True, "status": status, "user_id": row["user_id"]}
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
