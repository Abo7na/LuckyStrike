from telebot import types


def inline_home(lang='ar'):
    markup = types.InlineKeyboardMarkup()
    if lang == 'ar':
        markup.row(
            types.InlineKeyboardButton('🏠 الرئيسية', callback_data='home'),
            types.InlineKeyboardButton('💰 المحفظة', callback_data='nav_wallet'),
        )
    else:
        markup.row(
            types.InlineKeyboardButton('🏠 Home', callback_data='home'),
            types.InlineKeyboardButton('💰 Wallet', callback_data='nav_wallet'),
        )
    return markup
