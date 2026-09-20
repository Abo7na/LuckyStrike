import random
import sqlite3
from database.db import get_connection, get_setting, update_user_balance, record_transaction, get_user


def get_balance(user_id):
    user = get_user(user_id)
    return float(user["balance"]) if user else 0.0


def add_balance(user_id, amount, reference_id=None, description="ADMIN", admin_id=None):
    conn = get_connection()
    before = float(conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()["balance"])
    after = before + float(amount)
    conn.execute("UPDATE users SET balance = ? WHERE user_id = ?", (after, user_id))
    conn.commit()
    conn.close()
    record_transaction(user_id, "DEPOSIT", amount, before, after, reference_id, admin_id, description)
    return after


def deduct_balance(user_id, amount, reference_id=None, description="SYSTEM", admin_id=None):
    conn = get_connection()
    user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        return False
    before = float(user["balance"])
    if before < float(amount):
        return False
    after = before - float(amount)
    conn.execute("UPDATE users SET balance = ? WHERE user_id = ?", (after, user_id))
    conn.commit()
    conn.close()
    record_transaction(user_id, "GAME", amount, before, after, reference_id, admin_id, description)
    return True


def request_withdrawal(user_id, amount, method, account_details):
    conn = get_connection()
    user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        return {"ok": False, "message": "User not found"}
    balance = float(user["balance"])
    min_withdraw = float(get_setting("min_withdraw", "50"))
    if amount < min_withdraw:
        return {"ok": False, "message": f"Minimum withdrawal is {min_withdraw}"}
    if amount > balance:
        return {"ok": False, "message": "Insufficient balance"}
    if amount > float(get_setting("max_withdraw", "5000")):
        return {"ok": False, "message": "Maximum withdrawal exceeded"}
    conn.execute(
        "UPDATE users SET balance = balance - ? WHERE user_id = ?",
        (amount, user_id),
    )
    conn.execute(
        "INSERT INTO wallet_transactions(user_id, type, amount, balance_before, balance_after, reference_id, description) VALUES (?, 'WITHDRAW_PENDING', ?, ?, ?, ?, ?)",
        (user_id, amount, balance, balance - amount, f"wd_{user_id}_{int(random.random()*1000000)}", f"{method}:{account_details}"),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "message": "Withdrawal request created successfully."}


def approve_withdrawal(tx_ref, admin_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM wallet_transactions WHERE reference_id = ? AND type='WITHDRAW_PENDING'", (tx_ref,)).fetchone()
    if not row:
        conn.close()
        return {"ok": False, "message": "Request not found"}
    user_id = row["user_id"]
    amount = float(row["amount"])
    conn.execute("UPDATE wallet_transactions SET type = 'WITHDRAW', admin_id = ? WHERE reference_id = ?", (admin_id, tx_ref))
    conn.commit()
    conn.close()
    return {"ok": True, "message": f"Withdrawal {amount} approved"}
