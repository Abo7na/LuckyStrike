import random
from database.db import get_connection, get_setting


def upsert_referral_code(user_id, code):
    conn = get_connection()
    conn.execute("UPDATE users SET referral_code = ? WHERE user_id = ?", (code, user_id))
    conn.commit()
    conn.close()


def reward_referral(referrer_id, referred_user_id):
    conn = get_connection()
    reward = float(get_setting("referral_reward", "25"))
    reward_exists = conn.execute("SELECT * FROM referral_records WHERE referrer_id = ? AND referred_user_id = ?", (referrer_id, referred_user_id)).fetchone()
    if reward_exists:
        conn.close()
        return {"ok": False, "message": "Referral already rewarded"}
    conn.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, referrer_id))
    conn.execute("INSERT INTO referral_records(referrer_id, referred_user_id, reward) VALUES (?, ?, ?)", (referrer_id, referred_user_id, reward))
    conn.execute("INSERT INTO wallet_transactions(user_id, type, amount, balance_before, balance_after, description) VALUES (?, 'REFERRAL', ?, ?, ?, ?)", (referrer_id, reward, 0, reward, "Referral reward"))
    conn.commit()
    conn.close()
    return {"ok": True, "reward": reward}


def get_referral_summary(user_id):
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) as c FROM referral_records WHERE referrer_id = ?", (user_id,)).fetchone()["c"]
    total_reward = conn.execute("SELECT COALESCE(SUM(reward),0) as c FROM referral_records WHERE referrer_id = ?", (user_id,)).fetchone()["c"]
    user = conn.execute("SELECT referral_code FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return {"code": user["referral_code"] if user else "", "count": count, "total_reward": total_reward}
