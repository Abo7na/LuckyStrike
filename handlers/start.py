from keyboards.user import home_keyboard
from database.db import ensure_user, get_user, set_user_language
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def cmd_start(message):
        user = ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
        lang = user.get('language', 'ar')
        text = get_text(lang, 'welcome')
        bot.send_message(message.chat.id, text, reply_markup=home_keyboard(lang))

    @bot.message_handler(commands=['admin'])
    def cmd_admin(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        if user['is_admin'] != 1:
            bot.send_message(message.chat.id, get_text(user.get('language', 'ar'), 'not_allowed'))
            return
        bot.send_message(message.chat.id, "Admin panel", reply_markup=None)
