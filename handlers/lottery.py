from database.db import get_user, ensure_default_round
from handlers.start import register_handlers as start_register
from services.lottery_service import get_active_round, buy_ticket, draw_round
from keyboards.user import lottery_keyboard
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['lottery'])
    def lottery_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        ensure_default_round()
        round_data = get_active_round()
        lang = user.get('language', 'ar')
        if not round_data:
            bot.send_message(message.chat.id, get_text(lang, 'lottery_no_active'))
            return
        text = (
            f"<b>{get_text(lang, 'lottery')}</b>\n"
            f"Round: {round_data.get('title', 'Current')}\n"
            f"Ticket price: {round_data.get('ticket_price', 10)}\n"
            f"Max tickets: {round_data.get('max_tickets', 500)}"
        )
        bot.send_message(message.chat.id, text, reply_markup=lottery_keyboard(lang))

    @bot.callback_query_handler(func=lambda call: call.data == 'lottery_buy')
    def lottery_buy(call):
        user = get_user(call.from_user.id)
        if not user:
            return
        result = buy_ticket(call.from_user.id, 1)
        if result['ok']:
            bot.answer_callback_query(call.id, "Ticket purchased")
            bot.send_message(call.message.chat.id, "Ticket purchased successfully.")
        else:
            bot.answer_callback_query(call.id, result['message'])
