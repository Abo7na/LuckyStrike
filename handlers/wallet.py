from database.db import get_user
from keyboards.user import wallet_keyboard
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=["wallet"])
    def wallet_cmd(message):
        user = get_user(message.from_user.id)
        if user:
            lang = user.get("language", "ar")
            text = f"💰 <b>{get_text(lang, 'wallet')}</b>\n\nBalance: <code>{float(user['balance']):.2f}</code>"
            bot.send_message(message.chat.id, text, reply_markup=wallet_keyboard(lang))

    # Deposit and withdrawal callbacks are handled by the central navigation router.
