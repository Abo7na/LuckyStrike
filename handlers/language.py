from database.db import get_user, set_user_language
from keyboards.user import language_keyboard
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=["language"])
    def language_cmd(message):
        user = get_user(message.from_user.id)
        if user:
            bot.send_message(message.chat.id, get_text(user.get("language", "ar"), "language"), reply_markup=language_keyboard())
