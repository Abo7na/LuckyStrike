import random
import time
from database.db import get_connection, get_setting


def get_game_settings():
    conn = get_connection()
    settings = {
        "dice_price": float(get_setting("dice_price", "10")),
        "coin_price": float(get_setting("coin_price", "10")),
        "wheel_price": float(get_setting("wheel_price", "15")),
    }
    conn.close()
    return settings


def play_dice(user_id, bet_amount):
    conn = get_connection()
    user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user or float(user["balance"]) < float(bet_amount):
        conn.close()
        return {"ok": False, "message": "Insufficient balance"}
    result = random.randint(1, 6)
    winnings = 0
    if result in (4, 5, 6):
        winnings = float(bet_amount) * 2
    conn.execute("UPDATE users SET balance = balance - ? + ? WHERE user_id = ?", (bet_amount, winnings, user_id))
    conn.execute("INSERT INTO wallet_transactions(user_id, type, amount, balance_before, balance_after, description) VALUES (?, 'GAME_DICE', ?, ?, ?, ?)", (user_id, bet_amount, float(user["balance"]), float(user["balance"]) - float(bet_amount) + winnings, f"Dice result: {result}"))
    conn.commit()
    conn.close()
    return {"ok": True, "result": result, "winnings": winnings}


def play_coin(user_id, bet_amount):
    conn = get_connection()
    user = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user or float(user["balance"]) < float(bet_amount):
        conn.close()
        return {"ok": False, "message": "Insufficient balance"}
    side = random.choice(["heads", "tails"])
    winnings = float(bet_amount) * 2 if side == "heads" else 0
    conn.execute("UPDATE users SET balance = balance - ? + ? WHERE user_id = ?", (bet_amount, winnings, user_id))
    conn.execute("INSERT INTO wallet_transactions(user_id, type, amount, balance_before, balance_after, description) VALUES (?, 'GAME_COIN', ?, ?, ?, ?)", (user_id, bet_amount, float(user["balance"]), float(user["balance"]) - float(bet_amount) + winnings, f"Coin result: {side}"))
    conn.commit()
    conn.close()
    return {"ok": True, "result": side, "winnings": winnings}


def spin_wheel(user_id):
    conn = get_connection()
    user = conn.execute("SELECT balance, last_seen FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return {"ok": False, "message": "User not found"}
    wheel_cooldown = int(get_setting("wheel_cooldown_hours", "24"))
    # placeholder simple logic; last_seen is reused for cooldown demonstration
    result = random.choice(["small", "medium", "big", "jackpot"])
    rewards = {"small": 15, "medium": 50, "big": 120, "jackpot": 300}
    win = rewards[result]
    conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win, user_id))
    conn.execute("INSERT INTO wallet_transactions(user_id, type, amount, balance_before, balance_after, description) VALUES (?, 'WHEEL_WIN', ?, ?, ?, ?)", (user_id, win, float(user["balance"]), float(user["balance"]) + win, f"Wheel reward: {result}"))
    conn.commit()
    conn.close()
    return {"ok": True, "result": result, "reward": win}
