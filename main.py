# -*- coding: utf-8 -*-
import logging
import telebot

from config import BOT_TOKEN, ADMIN_IDS, APP_NAME
from database.db import init_db, ensure_default_round, ensure_user, set_user_language, get_dashboard_stats
from keyboards.user import home_keyboard, wallet_keyboard, games_keyboard, lottery_keyboard, language_keyboard, admin_keyboard, section_keyboard
from services.game_service import play_dice, play_coin, spin_wheel
from services.lottery_service import buy_ticket, get_active_round
from utils.helpers import get_text
from utils.locks import get_lock

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Copy .env.example to .env and configure it.")

init_db()
ensure_default_round()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("luckystrike")


def current_user(tg_user):
    return ensure_user(tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name)


def render(call, text, markup):
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    except Exception as exc:
        # Telegram rejects edits when text/markup is unchanged; send a fallback message.
        logger.debug("Could not edit message: %s", exc)
        bot.send_message(call.message.chat.id, text, reply_markup=markup)


def show_home(call):
    user = current_user(call.from_user)
    lang = user.get("language", "ar")
    return render(call, get_text(lang, "welcome"), home_keyboard(lang, call.from_user.id in ADMIN_IDS))


@bot.message_handler(commands=["help"])
def help_command(message):
    user = current_user(message.from_user)
    lang = user.get("language", "ar")
    bot.send_message(message.chat.id, get_text(lang, "welcome"), reply_markup=home_keyboard(lang, message.from_user.id in ADMIN_IDS))


@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    data = call.data or ""
    user = current_user(call.from_user)
    lang = user.get("language", "ar")
    try:
        bot.answer_callback_query(call.id)
        if data in {"nav_home", "home", "nav_back"}:
            return show_home(call)
        if data == "nav_wallet":
            return render(call, f"💰 <b>{get_text(lang, 'wallet')}</b>\n\nBalance: <code>{float(user['balance']):.2f}</code>", wallet_keyboard(lang))
        if data == "nav_games":
            return render(call, get_text(lang, "games"), games_keyboard(lang))
        if data == "nav_lottery":
            round_data = get_active_round()
            if not round_data:
                return render(call, get_text(lang, "lottery_no_active"), section_keyboard(lang))
            return render(call, f"🎟️ <b>{round_data['title']}</b>\n\nTicket price: <code>{float(round_data['ticket_price']):.2f}</code>\nTickets sold: <code>{round_data['tickets_sold']}</code>", lottery_keyboard(lang))
        if data == "nav_wheel":
            return render(call, get_text(lang, "wheel"), section_keyboard(lang, [telebot.types.InlineKeyboardButton("🎡 Spin", callback_data="wheel_spin")]))
        if data == "nav_language":
            return render(call, get_text(lang, "language"), language_keyboard())
        if data in {"set_lang_ar", "set_lang_en"}:
            new_lang = "ar" if data == "set_lang_ar" else "en"
            set_user_language(call.from_user.id, new_lang)
            return render(call, get_text(new_lang, "welcome"), home_keyboard(new_lang, call.from_user.id in ADMIN_IDS))
        if data == "nav_profile":
            return render(call, f"👤 <b>{get_text(lang, 'profile')}</b>\n\n🆔 <code>{user['user_id']}</code>\n💰 <code>{float(user['balance']):.2f}</code>\n📅 {user['created_at']}", section_keyboard(lang))
        if data == "nav_referral":
            return render(call, f"👥 <b>{get_text(lang, 'referral')}</b>\n\nCode: <code>{user.get('referral_code','')}</code>", section_keyboard(lang))
        if data == "nav_gifts":
            return render(call, get_text(lang, "gift_code") + "\n\nUse: /redeem CODE", section_keyboard(lang))
        if data == "nav_support":
            return render(call, get_text(lang, "support"), section_keyboard(lang))
        if data == "nav_my_bots":
            return render(call, "🤖 <b>بوتاتي</b>\n\nلا توجد بوتات مضافة حاليًا.", section_keyboard(lang))
        if data == "wallet_deposit":
            return render(call, "💳 <b>شحن يدوي</b>\n\nأرسل للإدارة المبلغ وطريقة الدفع ورقم العملية. لن يضاف الرصيد قبل الموافقة.", section_keyboard(lang))
        if data == "wallet_withdraw":
            return render(call, "💸 <b>سحب يدوي</b>\n\nأرسل المبلغ وطريقة السحب ومعلومات الحساب للإدارة. سيتم حجز المبلغ وإعادته تلقائيًا عند الرفض.", section_keyboard(lang))
        if data in {"game_dice", "game_coin"}:
            with get_lock(f"game:{call.from_user.id}"):
                result = play_dice(call.from_user.id, 10) if data == "game_dice" else play_coin(call.from_user.id, 10)
            text = result.get("message", "✅ تمت العملية") if not result.get("ok") else f"✅ النتيجة: <b>{result['result']}</b>\n💰 الجائزة: <code>{result['winnings']:.2f}</code>"
            return render(call, text, games_keyboard(lang))
        if data == "wheel_spin":
            with get_lock(f"wheel:{call.from_user.id}"):
                result = spin_wheel(call.from_user.id)
            text = result.get("message", "✅ تمت العملية") if not result.get("ok") else f"🎡 النتيجة: <b>{result['result']}</b>\n🎁 المكافأة: <code>{result['reward']:.2f}</code>"
            return render(call, text, section_keyboard(lang))
        if data == "lottery_buy":
            with get_lock(f"lottery:{call.from_user.id}"):
                result = buy_ticket(call.from_user.id)
            text = "✅ تم شراء التذكرة" if result.get("ok") else f"❌ {result.get('message')}"
            return render(call, text, lottery_keyboard(lang))
        if data == "admin_panel":
            if call.from_user.id not in ADMIN_IDS:
                return
            return render(call, "👑 <b>Admin Control Center</b>", admin_keyboard())
        if data.startswith("admin_"):
            if call.from_user.id not in ADMIN_IDS:
                return
            stats = get_dashboard_stats()
            return render(call, "📊 <b>Dashboard</b>\n\n" + "\n".join(f"• {key}: <code>{value}</code>" for key, value in stats.items()), admin_keyboard())
    except Exception:
        logger.exception("Callback failed: %s", data)
        bot.send_message(call.message.chat.id, "❌ حدث خطأ غير متوقع. تم تسجيل المشكلة، حاول مرة أخرى.")


# Message-command modules. Callback routing remains centralized above.
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
from handlers.admin.operations import register_handlers as register_admin_operations

register_start(bot)
register_user(bot)
register_wallet(bot)
register_lottery(bot)
register_games(bot)
register_wheel(bot)
register_gifts(bot)
register_referral(bot)
register_language(bot)
register_support(bot)
register_admin_operations(bot)

if __name__ == "__main__":
    print(f"🎰 {APP_NAME}\n✅ Database\n✅ Configuration\n🚀 Bot started")
    bot.infinity_polling(timeout=30, long_polling_timeout=30, skip_pending=True)
