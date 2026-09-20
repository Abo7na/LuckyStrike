from telebot import types


def admin_main_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton('Users', callback_data='admin_users'),
        types.InlineKeyboardButton('Wallet', callback_data='admin_wallet'),
    )
    markup.row(
        types.InlineKeyboardButton('Lottery', callback_data='admin_lottery'),
        types.InlineKeyboardButton('Stats', callback_data='admin_stats'),
    )
    return markup
