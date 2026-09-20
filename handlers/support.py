from database.db import get_user
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['support'])
    def support_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        lang = user.get('language', 'ar')
        bot.send_message(message.chat.id, get_text(lang, 'support'))
