from keyboards.admin import admin_main_keyboard
from config import ADMIN_IDS
from database.db import get_user


def register_handlers(bot):
    @bot.message_handler(commands=['stats'])
    def stats_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        bot.send_message(message.chat.id, "Statistics panel", reply_markup=admin_main_keyboard())
