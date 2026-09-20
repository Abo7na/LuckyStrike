import random
from datetime import datetime, timezone
from database.db import get_connection, get_setting


def get_game_settings():
    return {"dice_price": float(get_setting("dice_price", "10")), "coin_price": float(get_setting("coin_price", "10"))}


def _play(user_id, amount, label, result, winnings):
    conn = get_connection(); conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute("SELECT balance,is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row or row["is_banned"] or float(row["balance"]) < amount:
            conn.execute("ROLLBACK"); return {"ok": False, "message": "Insufficient balance"}
        before = float(row["balance"]); after = before - amount + winnings
        ref = f"game_{user_id}_{random.getrandbits(64)}"
        conn.execute("UPDATE users SET balance=? WHERE user_id=?", (after,user_id))
        conn.execute("INSERT INTO wallet_transactions(user_id,type,amount,balance_before,balance_after,reference_id,description) VALUES(?,?,?,?,?,?,?)", (user_id,label,amount,before,after,ref,f"Result: {result}; payout: {winnings}"))
        conn.execute("COMMIT"); return {"ok": True, "result": result, "winnings": winnings, "balance": after}
    except Exception:
        conn.execute("ROLLBACK"); raise
    finally: conn.close()


def play_dice(user_id, bet_amount):
    value = random.SystemRandom().randint(1,6); return _play(user_id,float(bet_amount),"GAME_DICE",value,float(bet_amount)*2 if value >= 4 else 0)


def play_coin(user_id, bet_amount):
    value = random.SystemRandom().choice(["heads","tails"]); return _play(user_id,float(bet_amount),"GAME_COIN",value,float(bet_amount)*2 if value == "heads" else 0)


def spin_wheel(user_id):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn = get_connection(); conn.execute("BEGIN IMMEDIATE")
    try:
        row = conn.execute("SELECT balance,last_spin_at,is_banned FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row or row["is_banned"]: conn.execute("ROLLBACK"); return {"ok": False, "message": "User unavailable"}
        if row["last_spin_at"]:
            previous = datetime.fromisoformat(row["last_spin_at"])
            elapsed = (datetime.fromisoformat(now) - previous).total_seconds()
            cooldown = int(get_setting("wheel_cooldown_hours", "24")) * 3600
            if elapsed < cooldown: conn.execute("ROLLBACK"); return {"ok": False, "message": f"Try again in {int((cooldown-elapsed)/3600)+1}h"}
        result = random.SystemRandom().choices(["small","medium","big","jackpot"],[60,25,12,3])[0]
        reward = {"small":15,"medium":50,"big":120,"jackpot":300}[result]; before=float(row["balance"]); after=before+reward
        ref=f"wheel_{user_id}_{random.getrandbits(64)}"
        conn.execute("UPDATE users SET balance=?,last_spin_at=? WHERE user_id=?", (after,now,user_id))
        conn.execute("INSERT INTO wallet_transactions(user_id,type,amount,balance_before,balance_after,reference_id,description) VALUES(?,?,?,?,?,?,?)", (user_id,"WHEEL_WIN",reward,before,after,ref,f"Wheel reward: {result}"))
        conn.execute("COMMIT"); return {"ok": True,"result":result,"reward":reward}
    except Exception:
        conn.execute("ROLLBACK"); raise
    finally: conn.close()
