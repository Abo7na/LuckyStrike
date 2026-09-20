from telebot import types


def home_keyboard(lang='ar'):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    items = [
        '💰 المحفظة', '🎟️ اليانصيب',
        '🎮 الألعاب', '🎡 العجلة',
        '🎁 الهدايا', '👥 الإحالة',
        '👤 حسابي', '🌐 اللغة',
        '📞 الإدارة', '🤖 بوتاتي',
    ]
    if lang == 'en':
        items = [
            '💰 Wallet', '🎟️ Lottery',
            '🎮 Games', '🎡 Wheel',
            '🎁 Gifts', '👥 Referral',
            '👤 Profile', '🌐 Language',
            '📞 Support', '🤖 My Bots',
        ]
    markup.add(*items)
    return markup


def wallet_keyboard(lang='ar'):
    markup = types.InlineKeyboardMarkup()
    if lang == 'ar':
        markup.add(types.InlineKeyboardButton('💳 شحن الرصيد', callback_data='wallet_deposit'))
        markup.add(types.InlineKeyboardButton('💸 سحب الرصيد', callback_data='wallet_withdraw'))
    else:
        markup.add(types.InlineKeyboardButton('💳 Deposit', callback_data='wallet_deposit'))
        markup.add(types.InlineKeyboardButton('💸 Withdraw', callback_data='wallet_withdraw'))
    return markup


def lottery_keyboard(lang='ar'):
    markup = types.InlineKeyboardMarkup()
    label = '🎫 Buy Ticket' if lang == 'en' else '🎫 شراء تذكرة'
    markup.add(types.InlineKeyboardButton(label, callback_data='lottery_buy'))
    return markup


def games_keyboard(lang='ar'):
    markup = types.InlineKeyboardMarkup()
    if lang == 'ar':
        markup.row(
            types.InlineKeyboardButton('🎲 النرد', callback_data='game_dice'),
            types.InlineKeyboardButton('🪙 الوجه/الكتابة', callback_data='game_coin'),
        )
        markup.row(
            types.InlineKeyboardButton('🎡 عجلة الحظ', callback_data='wheel_spin'),
        )
    else:
        markup.row(
            types.InlineKeyboardButton('🎲 Dice', callback_data='game_dice'),
            types.InlineKeyboardButton('🪙 Coin', callback_data='game_coin'),
        )
        markup.row(
            types.InlineKeyboardButton('🎡 Spin Wheel', callback_data='wheel_spin'),
        )
    return markup


def profile_keyboard(lang='ar'):
    markup = types.InlineKeyboardMarkup()
    label = '🌐 Language' if lang == 'en' else '🌐 اللغة'
    markup.add(types.InlineKeyboardButton(label, callback_data='nav_language'))
    return markup


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
