from telebot import types


def _button(text, callback):
    return types.InlineKeyboardButton(text, callback_data=callback)


def home_keyboard(lang="ar", is_admin=False):
    m = types.InlineKeyboardMarkup(row_width=2)
    if lang == "en":
        rows = [
            [_button("💰 Wallet", "nav_wallet"), _button("🎟️ Lottery", "nav_lottery")],
            [_button("🎮 Games", "nav_games"), _button("🎡 Wheel", "nav_wheel")],
            [_button("🎁 Gifts", "nav_gifts"), _button("👥 Referral", "nav_referral")],
            [_button("👤 Profile", "nav_profile"), _button("🌐 Language", "nav_language")],
            [_button("🤖 My Bots", "nav_my_bots"), _button("📞 Support", "nav_support")],
        ]
    else:
        rows = [
            [_button("💰 المحفظة", "nav_wallet"), _button("🎟️ اليانصيب", "nav_lottery")],
            [_button("🎮 الألعاب", "nav_games"), _button("🎡 عجلة الحظ", "nav_wheel")],
            [_button("🎁 الهدايا", "nav_gifts"), _button("👥 الإحالة", "nav_referral")],
            [_button("👤 حسابي", "nav_profile"), _button("🌐 اللغة", "nav_language")],
            [_button("🤖 بوتاتي", "nav_my_bots"), _button("📞 الإدارة", "nav_support")],
        ]
    for row in rows:
        m.row(*row)
    if is_admin:
        m.row(_button("👑 لوحة الإدارة", "admin_panel"))
    return m


def navigation_keyboard(lang="ar", back="nav_home", cancel="nav_cancel"):
    m = types.InlineKeyboardMarkup(row_width=2)
    back_text = "⬅️ Back" if lang == "en" else "⬅️ رجوع"
    home_text = "🏠 Home" if lang == "en" else "🏠 الرئيسية"
    cancel_text = "✖️ Cancel" if lang == "en" else "✖️ إلغاء"
    m.row(_button(back_text, back), _button(home_text, "nav_home"))
    if cancel:
        m.row(_button(cancel_text, cancel))
    return m


def section_keyboard(lang="ar", *buttons, back="nav_home", cancel=None):
    m = types.InlineKeyboardMarkup(row_width=2)
    for row in buttons:
        m.row(*row)
    back_text = "⬅️ Back" if lang == "en" else "⬅️ رجوع"
    home_text = "🏠 Home" if lang == "en" else "🏠 الرئيسية"
    m.row(_button(back_text, back), _button(home_text, "nav_home"))
    if cancel:
        cancel_text = "✖️ Cancel" if lang == "en" else "✖️ إلغاء"
        m.row(_button(cancel_text, cancel))
    return m


def wallet_keyboard(lang="ar"):
    if lang == "en":
        return section_keyboard(lang, [_button("💳 Deposit", "wallet_deposit"), _button("💸 Withdraw", "wallet_withdraw")], [_button("📒 Transactions", "wallet_transactions")])
    return section_keyboard(lang, [_button("💳 شحن الرصيد", "wallet_deposit"), _button("💸 سحب الرصيد", "wallet_withdraw")], [_button("📒 سجل العمليات", "wallet_transactions")])


def games_keyboard(lang="ar"):
    if lang == "en":
        return section_keyboard(lang, [_button("🎲 Dice", "game_dice"), _button("🪙 Coin", "game_coin")], [_button("🎡 Wheel", "nav_wheel")])
    return section_keyboard(lang, [_button("🎲 النرد", "game_dice"), _button("🪙 وجه/كتابة", "game_coin")], [_button("🎡 العجلة", "nav_wheel")])


def lottery_keyboard(lang="ar"):
    label = "🎫 Buy ticket" if lang == "en" else "🎫 شراء تذكرة"
    info = "📊 Round info" if lang == "en" else "📊 معلومات الجولة"
    return section_keyboard(lang, [_button(label, "lottery_buy"), _button(info, "lottery_info")])


def language_keyboard():
    return section_keyboard("ar", [_button("🇸🇾 العربية", "set_lang_ar"), _button("🇬🇧 English", "set_lang_en")])


def profile_keyboard(lang="ar"):
    language_text = "🌐 Language" if lang == "en" else "🌐 اللغة"
    return section_keyboard(lang, [_button(language_text, "nav_language")])


def admin_keyboard():
    return section_keyboard(
        "ar",
        [_button("📊 الإحصائيات", "admin_stats"), _button("👥 المستخدمون", "admin_users")],
        [_button("💰 المحفظة", "admin_wallet"), _button("🎟️ اليانصيب", "admin_lottery")],
        [_button("⚙️ الإعدادات", "admin_settings"), _button("🛡️ الأمان", "admin_security")],
        [_button("📥 الطلبات", "admin_pending"), _button("💾 نسخة احتياطية", "admin_backup")],
    )
