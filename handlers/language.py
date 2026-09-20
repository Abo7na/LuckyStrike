from database.db import get_user, set_user_language
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['language'])
    def language_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        lang = user.get('language', 'ar')
        bot.send_message(message.chat.id, get_text(lang, 'language'), reply_markup=None)

    @bot.callback_query_handler(func=lambda call: call.data in {'set_lang_ar', 'set_lang_en'})
    def set_lang(call):
        lang = 'ar' if call.data == 'set_lang_ar' else 'en'
        set_user_language(call.from_user.id, lang)
        bot.answer_callback_query(call.id, f"Language changed to {lang}")
