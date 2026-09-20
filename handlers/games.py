from utils.helpers import get_text
from database.db import get_user
from services.game_service import play_dice, play_coin, spin_wheel
from keyboards.user import games_keyboard


def register_handlers(bot):
    @bot.message_handler(commands=['games'])
    def games_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        lang = user.get('language', 'ar')
        bot.send_message(message.chat.id, get_text(lang, 'games'), reply_markup=games_keyboard(lang))

    @bot.callback_query_handler(func=lambda call: call.data == 'game_dice')
    def game_dice(call):
        result = play_dice(call.from_user.id, 10)
        if result['ok']:
            bot.answer_callback_query(call.id, f"Dice result: {result['result']} | Winnings: {result['winnings']}")
        else:
            bot.answer_callback_query(call.id, result['message'])

    @bot.callback_query_handler(func=lambda call: call.data == 'game_coin')
    def game_coin(call):
        result = play_coin(call.from_user.id, 10)
        if result['ok']:
            bot.answer_callback_query(call.id, f"Coin result: {result['result']} | Winnings: {result['winnings']}")
        else:
            bot.answer_callback_query(call.id, result['message'])
