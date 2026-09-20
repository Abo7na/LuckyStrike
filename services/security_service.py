import os
import logging
from datetime import datetime

logger = logging.getLogger("luckystrike")
logger.setLevel(logging.INFO)
if not logger.handlers:
    os.makedirs("logs", exist_ok=True)
    handler = logging.FileHandler("logs/security.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_security(event):
    logger.warning(event)


def is_admin(user_id, admin_ids):
    return user_id in admin_ids


def is_valid_user_id(user_id):
    try:
        return int(user_id) > 0
    except (TypeError, ValueError):
        return False
