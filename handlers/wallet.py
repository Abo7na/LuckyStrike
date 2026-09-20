from database.db import get_user, get_setting, set_setting, log_admin_action, record_transaction
from keyboards.user import wallet_keyboard
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['wallet'])
    def wallet_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        lang = user.get('language', 'ar')
        text = f"<b>{get_text(lang, 'wallet')}</b>\nBalance: {user['balance']}\nMin withdraw: {get_setting('min_withdraw', '50')}"
        bot.send_message(message.chat.id, text, reply_markup=wallet_keyboard(lang))

    @bot.callback_query_handler(func=lambda call: call.data == 'wallet_deposit')
    def wallet_deposit(call):
        bot.answer_callback_query(call.id, "Deposit requests are reviewed by admin.")
        bot.send_message(call.message.chat.id, "Send the amount and payment reference. Example: 100 | ShamCash")
