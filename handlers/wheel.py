from database.db import get_user
from keyboards.user import section_keyboard
from utils.helpers import get_text
from telebot import types


def register_handlers(bot):
    @bot.message_handler(commands=["wheel"])
    def wheel_cmd(message):
        user = get_user(message.from_user.id)
        if user:
            lang = user.get("language", "ar")
            label = "🎡 Spin now" if lang == "en" else "🎡 أدر العجلة الآن"
            bot.send_message(message.chat.id, get_text(lang, "wheel"), reply_markup=section_keyboard(lang, [types.InlineKeyboardButton(label, callback_data="wheel_spin")]))
