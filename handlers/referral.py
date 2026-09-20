from database.db import get_user
from services.referral_service import get_referral_summary
from utils.helpers import get_text


def register_handlers(bot):
    @bot.message_handler(commands=['referral'])
    def referral_cmd(message):
        user = get_user(message.from_user.id)
        if not user:
            return
        summary = get_referral_summary(message.from_user.id)
        text = (
            f"<b>{get_text(user.get('language', 'ar'), 'referral')}</b>\n"
            f"Code: {summary['code']}\n"
            f"Friends: {summary['count']}\n"
            f"Reward total: {summary['total_reward']}"
        )
        bot.send_message(message.chat.id, text)
