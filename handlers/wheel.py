from database.db import get_user
from keyboards.user import section_keyboard
from telebot import types
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=["wheel"])
    def wheel_cmd(message):
        user = get_user(message.from_user.id)
        if user:
            lang = user.get("language", "ar")
            label = "🎡 Spin now" if lang == "en" else "🎡 أدر العجلة الآن"
            markup = section_keyboard(lang, [types.InlineKeyboardButton(label, callback_data="wheel_spin")])
            bot.send_message(message.chat.id, get_text(lang, "wheel"), reply_markup=markup)
