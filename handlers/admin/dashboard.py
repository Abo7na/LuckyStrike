from database.db import get_user, get_dashboard_stats, log_admin_action
from config import ADMIN_IDS
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['adminpanel'])
    def admin_panel(message):
        user = get_user(message.from_user.id)
        if not user or message.from_user.id not in ADMIN_IDS:
            return
        stats = get_dashboard_stats()
        text = (
            "<b>Admin Dashboard</b>\n"
            f"Users: {stats['total_users']}\n"
            f"Total_balance: {stats['total_balance']}\n"
            f"Deposits: {stats['total_deposits']}\n"
            f"Withdrawals: {stats['total_withdrawals']}\n"
            f"Total tickets: {stats['total_tickets']}\n"
            f"Gift use: {stats['gift_usage']}\n"
            f"Referrals: {stats['referrals']}"
        )
        bot.send_message(message.chat.id, text)
