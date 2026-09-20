from database.db import get_user, ensure_default_round
from keyboards.user import lottery_keyboard
from services.lottery_service import get_active_round
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=["lottery"])
    def lottery_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        ensure_default_round()
        round_data = get_active_round()
        lang = user.get("language", "ar")
        if not round_data:
            bot.send_message(message.chat.id, get_text(lang, "lottery_no_active"))
            return
        bot.send_message(message.chat.id, f"🎟️ <b>{round_data['title']}</b>\n\nTicket price: <code>{float(round_data['ticket_price']):.2f}</code>\nTickets sold: <code>{round_data['tickets_sold']}</code>", reply_markup=lottery_keyboard(lang))
