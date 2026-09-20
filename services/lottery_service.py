import random
import sqlite3
from database.db import get_connection, get_setting
from services.wallet_service import deduct_balance


def get_active_round():
    conn = get_connection()
    row = conn.execute("SELECT * FROM lottery_rounds WHERE status = 'ACTIVE' ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row is not None else None


def create_round(title=None):
    ticket_price = float(get_setting("ticket_price", "10"))
    conn = get_connection()
    conn.execute(
        "INSERT INTO lottery_rounds(title, ticket_price, max_tickets, status, start_time, end_time) VALUES (?, ?, ?, 'ACTIVE', CURRENT_TIMESTAMP, datetime(CURRENT_TIMESTAMP, '+7 days'))",
        (title or f"Lucky Strike Round #{int(time.time())}", ticket_price, 500),
    )
    conn.commit()
    conn.close()


def buy_ticket(user_id, round_id=None):
    conn = get_connection()
    round_row = conn.execute("SELECT * FROM lottery_rounds WHERE id = ? AND status='ACTIVE'", (round_id or 1,)).fetchone()
    if not round_row:
        return {"ok": False, "message": "No active round"}
    ticket_price = float(round_row["ticket_price"])
    user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user or float(user["balance"]) < ticket_price:
        return {"ok": False, "message": "Insufficient balance"}
    ticket_number = int(random.random() * 1000000)
    conn.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (ticket_price, user_id))
    conn.execute(
        "INSERT INTO lottery_tickets(round_id, user_id, ticket_number, price) VALUES (?, ?, ?, ?)",
        (round_row["id"], user_id, ticket_number, ticket_price),
    )
    conn.execute(
        "INSERT INTO wallet_transactions(user_id, type, amount, balance_before, balance_after, description) VALUES (?, 'LOTTERY_TICKET', ?, ?, ?, ?)",
        (user_id, ticket_price, float(user["balance"]), float(user["balance"]) - ticket_price, "Lottery ticket purchase"),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "message": "Ticket purchased successfully"}


def draw_round(round_id):
    conn = get_connection()
    tickets = conn.execute("SELECT * FROM lottery_tickets WHERE round_id = ? ORDER BY id", (round_id,)).fetchall()
    if not tickets:
        conn.close()
        return {"ok": False, "message": "No tickets"}
    winner = random.choice(tickets)
    conn.execute("UPDATE lottery_tickets SET is_winner = 1 WHERE id = ?", (winner["id"],))
    conn.execute("UPDATE lottery_rounds SET status = 'COMPLETED' WHERE id = ?", (round_id,))
    conn.commit()
    conn.close()
    return {"ok": True, "winner_user_id": winner["user_id"], "ticket_id": winner["id"]}
