from database.db import get_user
from keyboards.user import games_keyboard
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=["games"])
    def games_cmd(message):
        user = get_user(message.from_user.id)
        if user:
            lang = user.get("language", "ar")
            bot.send_message(message.chat.id, get_text(lang, "games"), reply_markup=games_keyboard(lang))
