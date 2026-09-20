from config import ADMIN_IDS


def register_handlers(bot):
    @bot.message_handler(commands=['security'])
    def security_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        bot.send_message(message.chat.id, "Security controls loaded.")
