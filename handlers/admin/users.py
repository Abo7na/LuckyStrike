from database.db import get_user, log_admin_action
from config import ADMIN_IDS


def register_handlers(bot):
    @bot.message_handler(commands=['users'])
    def users_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        bot.send_message(message.chat.id, "Users list is available in the admin dashboard.")
