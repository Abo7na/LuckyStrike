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

    @bot.message_handler(commands=["approve", "reject"])
    def decide_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, f"Usage: /{message.text.split()[0][1:]} REQUEST_ID")
            return
        approve = message.text.split()[0].lower() == "/approve"
        request_id = parts[1].strip()
        result = decide_request(request_id, message.from_user.id, approve, "Approved by admin" if approve else "Rejected by admin")
        log_admin_action(message.from_user.id, "approve_wallet_request" if approve else "reject_wallet_request", details=request_id)
        bot.send_message(message.chat.id, ("✅ Request approved" if approve else "✅ Request rejected/refunded") if result.get("ok") else f"❌ {result.get('message')}")
