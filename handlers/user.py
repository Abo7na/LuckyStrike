from keyboards.user import profile_keyboard
from database.db import get_user
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['profile'])
    def profile_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        lang = user.get('language', 'ar')
        text = (
            f"<b>{get_text(lang, 'profile')}</b>\n"
            f"ID: {user['user_id']}\n"
            f"Username: @{user['username'] or 'n/a'}\n"
            f"Balance: {user['balance']}\n"
            f"Language: {lang.upper()}"
        )
        bot.send_message(message.chat.id, text, reply_markup=profile_keyboard(lang))
