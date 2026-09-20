# -*- coding: utf-8 -*-
import time
from datetime import datetime, timezone
from telebot import TeleBot

from config import BOT_TOKEN, ADMIN_IDS, APP_NAME
from database.db import init_db, ensure_user, get_user, set_user_language, get_dashboard_stats
from keyboards.user import home_keyboard, wallet_keyboard, games_keyboard, lottery_keyboard, language_keyboard, admin_keyboard, section_keyboard
from services.game_service import play_dice, play_coin, spin_wheel
from services.lottery_service import buy_ticket, get_active_round
from utils.helpers import get_text
from utils.locks import get_lock

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Copy .env.example to .env and configure it.")

init_db()
bot = TeleBot(BOT_TOKEN, parse_mode="HTML")


def user_for(tg_user):
    return ensure_user(tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name)


def render(call, text, markup):
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    except Exception:
        bot.send_message(call.message.chat.id, text, reply_markup=markup)


def panel(call):
    user = user_for(call.from_user)
    lang = user.get("language", "ar")
    render(call, get_text(lang, "welcome"), home_keyboard(lang, call.from_user.id in ADMIN_IDS))


@bot.message_handler(commands=["help"])
def help_command(message):
    user = user_for(message.from_user)
    bot.send_message(message.chat.id, get_text(user.get("language", "ar"), "welcome"), reply_markup=home_keyboard(user.get("language", "ar"), message.from_user.id in ADMIN_IDS))


@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    data = call.data or ""
    user = user_for(call.from_user)
    lang = user.get("language", "ar")
    try:
        bot.answer_callback_query(call.id)
        if data in {"nav_home", "home", "nav_back"}:
            return panel(call)
        if data == "nav_wallet":
            return render(call, f"💰 <b>{get_text(lang, 'wallet')}</b>\n\nBalance: <code>{user['balance']:.2f}</code>", wallet_keyboard(lang))
        if data == "nav_games":
            return render(call, get_text(lang, "games"), games_keyboard(lang))
        if data == "nav_lottery":
            round_data = get_active_round()
            if not round_data:
                return render(call, get_text(lang, "lottery_no_active"), section_keyboard(lang))
            return render(call, f"🎟️ <b>{round_data['title']}</b>\n\nTicket price: <code>{round_data['ticket_price']:.2f}</code>", lottery_keyboard(lang))
        if data == "nav_wheel":
            return render(call, get_text(lang, "wheel"), section_keyboard(lang, [__import__('telebot').types.InlineKeyboardButton('🎡 Spin', callback_data='wheel_spin')]))
        if data == "nav_language":
            return render(call, get_text(lang, "language"), language_keyboard())
        if data == "set_lang_ar" or data == "set_lang_en":
            new_lang = "ar" if data.endswith("ar") else "en"
            set_user_language(call.from_user.id, new_lang)
            return render(call, get_text(new_lang, "welcome"), home_keyboard(new_lang, call.from_user.id in ADMIN_IDS))
        if data == "nav_profile":
            return render(call, f"👤 <b>{get_text(lang, 'profile')}</b>\n\n🆔 <code>{user['user_id']}</code>\n💰 <code>{user['balance']:.2f}</code>\n📅 {user['created_at']}", section_keyboard(lang))
        if data == "nav_referral":
            return render(call, f"👥 <b>{get_text(lang, 'referral')}</b>\n\nCode: <code>{user.get('referral_code','')}</code>", section_keyboard(lang))
        if data == "nav_gifts":
            return render(call, get_text(lang, "gift_code") + "\n\nUse: /redeem CODE", section_keyboard(lang))
        if data == "nav_support":
            return render(call, get_text(lang, "support"), section_keyboard(lang))
        if data == "nav_my_bots":
            return render(call, "🤖 <b>بوتاتي</b>\n\nلا توجد بوتات مضافة حاليًا.", section_keyboard(lang))
        if data == "wallet_deposit":
            return render(call, "💳 <b>شحن الرصيد يدويًا</b>\n\nحوّل المبلغ عبر طريقة الدفع المتفق عليها، ثم أرسل للإدارة المبلغ ورقم العملية. لن يضاف الرصيد قبل المراجعة.", section_keyboard(lang))
        if data == "wallet_withdraw":
            return render(call, "💸 <b>السحب اليدوي</b>\n\nأرسل للإدارة المبلغ، الطريقة، ومعلومات الحساب. سيتم حجز المبلغ ومراجعته يدويًا.", section_keyboard(lang))
        if data == "game_dice" or data == "game_coin":
            with get_lock(f"game:{call.from_user.id}"):
                result = play_dice(call.from_user.id, 10) if data == "game_dice" else play_coin(call.from_user.id, 10)
            msg = result.get("message", "✅ تمت العملية") if not result.get("ok") else f"✅ النتيجة: <b>{result['result']}</b>\n💰 الجائزة: <code>{result['winnings']:.2f}</code>"
            return render(call, msg, games_keyboard(lang))
        if data == "wheel_spin":
            with get_lock(f"wheel:{call.from_user.id}"):
                result = spin_wheel(call.from_user.id)
            msg = result.get("message", "✅ تمت العملية") if not result.get("ok") else f"🎡 النتيجة: <b>{result['result']}</b>\n🎁 المكافأة: <code>{result['reward']:.2f}</code>"
            return render(call, msg, section_keyboard(lang))
        if data == "lottery_buy":
            with get_lock(f"lottery:{call.from_user.id}"):
                result = buy_ticket(call.from_user.id)
            return render(call, "✅ تم شراء التذكرة" if result.get("ok") else f"❌ {result.get('message')}", lottery_keyboard(lang))
        if data.startswith("admin"):
            if call.from_user.id not in ADMIN_IDS:
                return
            if data == "admin_panel":
                return render(call, "👑 <b>Admin Control Center</b>", admin_keyboard())
            stats = get_dashboard_stats()
            return render(call, "📊 <b>Dashboard</b>\n\n" + "\n".join(f"• {k}: <code>{v}</code>" for k, v in stats.items()), admin_keyboard())
    except Exception:
        bot.send_message(call.message.chat.id, "❌ حدث خطأ غير متوقع. تم تسجيل المشكلة، حاول مرة أخرى.")


# Message-based feature modules contain only slash commands; callbacks are centralized above.
from handlers.start import register_handlers as register_start
from handlers.user import register_handlers as register_user
from handlers.wallet import register_handlers as register_wallet
from handlers.lottery import register_handlers as register_lottery
from handlers.games import register_handlers as register_games
from handlers.wheel import register_handlers as register_wheel
from handlers.gifts import register_handlers as register_gifts
from handlers.referral import register_handlers as register_referral
from handlers.language import register_handlers as register_language
from handlers.support import register_handlers as register_support
register_start(bot); register_user(bot); register_wallet(bot); register_lottery(bot); register_games(bot); register_wheel(bot); register_gifts(bot); register_referral(bot); register_language(bot); register_support(bot)

if __name__ == "__main__":
    print(f"🎰 {APP_NAME}\n✅ Database\n✅ Configuration\n🚀 Bot started")
    bot.infinity_polling(timeout=30, long_polling_timeout=30, skip_pending=True)
