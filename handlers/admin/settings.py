from database.db import get_user
from config import ADMIN_IDS


def register_handlers(bot):
    @bot.message_handler(commands=['settings'])
    def settings_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        bot.send_message(message.chat.id, "Admin settings screen is ready to be expanded.")
