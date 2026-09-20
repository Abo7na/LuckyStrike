from config import ADMIN_IDS
from database.db import get_user
from keyboards.user import wallet_keyboard
from services.wallet_service import create_deposit_request, request_withdrawal
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=["wallet"])
    def wallet_cmd(message):
        user = get_user(message.from_user.id)
        if user:
            lang = user.get("language", "ar")
            text = f"💰 <b>{get_text(lang, 'wallet')}</b>\n\nBalance: <code>{float(user['balance']):.2f}</code>"
            bot.send_message(message.chat.id, text, reply_markup=wallet_keyboard(lang))

    def receive_deposit(message):
        try:
            amount, method, reference = [part.strip() for part in message.text.split("|", 2)]
            result = create_deposit_request(message.from_user.id, float(amount), method, reference)
            if result["ok"]:
                bot.send_message(message.chat.id, f"✅ تم إنشاء طلب الشحن.\nرقم الطلب: <code>{result['request_id']}</code>")
            else:
                bot.send_message(message.chat.id, f"❌ {result['message']}")
        except (ValueError, TypeError):
            bot.send_message(message.chat.id, "❌ الصيغة الصحيحة: المبلغ | الطريقة | رقم العملية")

    def receive_withdraw(message):
        try:
            amount, method, account = [part.strip() for part in message.text.split("|", 2)]
            result = request_withdrawal(message.from_user.id, float(amount), method, account)
            if result["ok"]:
                bot.send_message(message.chat.id, f"✅ تم حجز المبلغ وإنشاء طلب السحب.\nرقم الطلب: <code>{result['request_id']}</code>")
            else:
                bot.send_message(message.chat.id, f"❌ {result['message']}")
        except (ValueError, TypeError):
            bot.send_message(message.chat.id, "❌ الصيغة الصحيحة: المبلغ | الطريقة | معلومات الحساب")

    @bot.callback_query_handler(func=lambda call: call.data == "wallet_deposit")
    def wallet_deposit(call):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💳 أرسل: المبلغ | طريقة الدفع | رقم العملية\nمثال: 100 | ShamCash | ABC123")
        bot.register_next_step_handler(call.message, receive_deposit)

    @bot.callback_query_handler(func=lambda call: call.data == "wallet_withdraw")
    def wallet_withdraw(call):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💸 أرسل: المبلغ | طريقة السحب | معلومات الحساب\nمثال: 100 | MTN | 09XXXXXXXX")
        bot.register_next_step_handler(call.message, receive_withdraw)
