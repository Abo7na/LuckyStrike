import os
import json
from datetime import datetime


def send_notification(user_id, message):
    # Placeholder logging method; in a real deployment this can be a push API or admin channel.
    os.makedirs("logs", exist_ok=True)
    with open("logs/notifications.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()} | user={user_id} | {message}\n")
    return True
