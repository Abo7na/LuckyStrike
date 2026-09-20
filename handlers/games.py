from database.db import get_user
from keyboards.user import games_keyboard
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=["games"])
    def games_cmd(message):
        user = get_user(message.from_user.id)
        if user:
            bot.send_message(message.chat.id, get_text(user.get("language", "ar"), "games"), reply_markup=games_keyboard(user.get("language", "ar")))
