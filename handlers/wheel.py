from database.db import get_user
from services.game_service import spin_wheel
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['wheel'])
    def wheel_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        bot.send_message(message.chat.id, get_text(user.get('language', 'ar'), 'wheel'))

    @bot.callback_query_handler(func=lambda call: call.data == 'wheel_spin')
    def wheel_spin(call):
        result = spin_wheel(call.from_user.id)
        if result['ok']:
            bot.answer_callback_query(call.id, f"Wheel: {result['result']} | Reward: {result['reward']}")
        else:
            bot.answer_callback_query(call.id, result['message'])
