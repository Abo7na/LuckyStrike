from config import ADMIN_IDS
from database.db import get_dashboard_stats, log_admin_action
from services.wallet_service import decide_request


def register_handlers(bot):
    @bot.message_handler(commands=["stats"])
    def stats_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        stats = get_dashboard_stats()
        bot.send_message(message.chat.id, "📊 <b>Statistics</b>\n\n" + "\n".join(f"• {key}: <code>{value}</code>" for key, value in stats.items()))

    @bot.message_handler(commands=["approve"])
    def approve_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "Usage: /approve REQUEST_ID")
            return
        result = decide_request(parts[1].strip(), message.from_user.id, True, "Approved by admin")
        log_admin_action(message.from_user.id, "approve_wallet_request", details=parts[1].strip())
        bot.send_message(message.chat.id, "✅ Request approved" if result.get("ok") else f"❌ {result.get('message')}")

    @bot.message_handler(commands=["reject"])
    def reject_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "Usage: /reject REQUEST_ID")
            return
        result = decide_request(parts[1].strip(), message.from_user.id, False, "Rejected by admin")
        log_admin_action(message.from_user.id, "reject_wallet_request", details=parts[1].strip())
        bot.send_message(message.chat.id, "✅ Request rejected/refunded when applicable" if result.get("ok") else f"❌ {result.get('message')}")
