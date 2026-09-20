import random
import time
from database.db import get_connection, get_setting


def get_active_round():
    conn=get_connection(); row=conn.execute("SELECT r.*,COUNT(t.id) tickets_sold FROM lottery_rounds r LEFT JOIN lottery_tickets t ON t.round_id=r.id WHERE r.status='ACTIVE' GROUP BY r.id ORDER BY r.id DESC LIMIT 1").fetchone(); conn.close()
    return dict(row) if row else None


def buy_ticket(user_id, round_id=None):
    conn=get_connection(); conn.execute("BEGIN IMMEDIATE")
    try:
        row=conn.execute("SELECT * FROM lottery_rounds WHERE status='ACTIVE' AND (? IS NULL OR id=?) ORDER BY id DESC LIMIT 1", (round_id,round_id)).fetchone()
        if not row: conn.execute("ROLLBACK"); return {"ok":False,"message":"No active round"}
        count=conn.execute("SELECT COUNT(*) c FROM lottery_tickets WHERE round_id=?",(row["id"],)).fetchone()["c"]
        if count >= row["max_tickets"]: conn.execute("ROLLBACK"); return {"ok":False,"message":"Round is full"}
        user=conn.execute("SELECT balance,is_banned FROM users WHERE user_id=?",(user_id,)).fetchone(); price=float(row["ticket_price"])
        if not user or user["is_banned"] or float(user["balance"])<price: conn.execute("ROLLBACK"); return {"ok":False,"message":"Insufficient balance"}
        before=float(user["balance"]); after=before-price; ticket_number=conn.execute("SELECT COALESCE(MAX(ticket_number),0)+1 n FROM lottery_tickets WHERE round_id=?",(row["id"],)).fetchone()["n"]
        reference=f"lottery_{user_id}_{random.getrandbits(64)}"
        conn.execute("UPDATE users SET balance=? WHERE user_id=?",(after,user_id)); conn.execute("INSERT INTO lottery_tickets(round_id,user_id,ticket_number,price) VALUES(?,?,?,?)",(row["id"],user_id,ticket_number,price)); conn.execute("INSERT INTO wallet_transactions(user_id,type,amount,balance_before,balance_after,reference_id,description) VALUES(?,?,?,?,?,?,?)",(user_id,"LOTTERY",price,before,after,reference,f"Ticket #{ticket_number}")); conn.execute("COMMIT"); return {"ok":True,"ticket_number":ticket_number}
    except Exception:
        conn.execute("ROLLBACK"); raise
    finally: conn.close()


def draw_round(round_id):
    conn=get_connection(); conn.execute("BEGIN IMMEDIATE")
    try:
        round_row=conn.execute("SELECT * FROM lottery_rounds WHERE id=? AND status='ACTIVE'",(round_id,)).fetchone(); tickets=conn.execute("SELECT * FROM lottery_tickets WHERE round_id=?",(round_id,)).fetchall()
        if not round_row or not tickets: conn.execute("ROLLBACK"); return {"ok":False,"message":"Round unavailable or empty"}
        winner=random.SystemRandom().choice(tickets); conn.execute("UPDATE lottery_tickets SET is_winner=1 WHERE id=?",(winner["id"],)); conn.execute("UPDATE lottery_rounds SET status='COMPLETED' WHERE id=?",(round_id,)); conn.execute("COMMIT"); return {"ok":True,"winner_user_id":winner["user_id"],"ticket_id":winner["id"]}
    except Exception:
        conn.execute("ROLLBACK"); raise
    finally: conn.close()
