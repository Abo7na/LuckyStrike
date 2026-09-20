from database.db import get_user
from services.gift_service import redeem_gift_code
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['gifts'])
    def gifts_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        msg = get_text(user.get('language', 'ar'), 'gift_code')
        bot.send_message(message.chat.id, msg)

    @bot.message_handler(func=lambda message: message.text and message.text.startswith('/redeem '))
    def redeem_cmd(message):
        code = message.text.split(None, 1)[1].strip().upper()
        result = redeem_gift_code(message.from_user.id, code)
        if result['ok']:
            bot.send_message(message.chat.id, f"Gift redeemed: {result['amount']}")
        else:
            bot.send_message(message.chat.id, result['message'])
