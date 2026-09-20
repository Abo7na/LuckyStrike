from config import ADMIN_IDS
from database.db import ensure_user
from keyboards.user import home_keyboard, admin_keyboard
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=["start"])
    def cmd_start(message):
        user = ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
        lang = user.get("language", "ar")
        bot.send_message(message.chat.id, get_text(lang, "welcome"), reply_markup=home_keyboard(lang, message.from_user.id in ADMIN_IDS))

    @bot.message_handler(commands=["admin", "panel", "a"])
    def cmd_admin(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        bot.send_message(message.chat.id, "👑 <b>Admin Control Center</b>", reply_markup=admin_keyboard())
