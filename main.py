# -*- coding: utf-8 -*-
import logging
import telebot

from config import BOT_TOKEN, ADMIN_IDS, APP_NAME
from database.db import init_db, ensure_default_round, ensure_user, set_user_language, get_dashboard_stats, get_connection
from keyboards.user import home_keyboard, wallet_keyboard, games_keyboard, lottery_keyboard, language_keyboard, admin_keyboard, section_keyboard
from services.game_service import play_dice, play_coin, spin_wheel
from services.lottery_service import buy_ticket, get_active_round
from services.wallet_service import create_deposit_request, request_withdrawal
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
        logger.debug("message edit fallback: %s", exc)
        bot.send_message(call.message.chat.id, text, reply_markup=markup)


def show_home(call):
    user = current_user(call.from_user)
    lang = user.get("language", "ar")
    return render(call, get_text(lang, "welcome"), home_keyboard(lang, call.from_user.id in ADMIN_IDS))


def prompt_with_cancel(call, text, callback):
    markup = section_keyboard("ar", cancel="nav_cancel")
    sent = bot.send_message(call.message.chat.id, text, reply_markup=markup)
    bot.register_next_step_handler(sent, callback)


def receive_deposit(message):
    if not message.text or message.text.strip().lower() in {"cancel", "إلغاء", "/cancel"}:
        bot.send_message(message.chat.id, "✖️ تم الإلغاء.")
        return
    try:
        amount, method, reference = [p.strip() for p in message.text.split("|", 2)]
        result = create_deposit_request(message.from_user.id, float(amount), method, reference)
        bot.send_message(message.chat.id, f"✅ تم إنشاء طلب الشحن: <code>{result['request_id']}</code>" if result.get("ok") else f"❌ {result.get('message')}")
    except (ValueError, TypeError):
        bot.send_message(message.chat.id, "❌ الصيغة: المبلغ | الطريقة | رقم العملية\nأرسل /cancel للإلغاء.")


def receive_withdraw(message):
    if not message.text or message.text.strip().lower() in {"cancel", "إلغاء", "/cancel"}:
        bot.send_message(message.chat.id, "✖️ تم الإلغاء.")
        return
    try:
        amount, method, account = [p.strip() for p in message.text.split("|", 2)]
        result = request_withdrawal(message.from_user.id, float(amount), method, account)
        bot.send_message(message.chat.id, f"✅ تم حجز المبلغ وإنشاء طلب السحب: <code>{result['request_id']}</code>" if result.get("ok") else f"❌ {result.get('message')}")
    except (ValueError, TypeError):
        bot.send_message(message.chat.id, "❌ الصيغة: المبلغ | الطريقة | معلومات الحساب\nأرسل /cancel للإلغاء.")


@bot.message_handler(commands=["help", "cancel"])
def command_help(message):
    user = current_user(message.from_user)
    if message.text.startswith("/cancel"):
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "✖️ تم إلغاء العملية.", reply_markup=home_keyboard(user.get("language", "ar"), message.from_user.id in ADMIN_IDS))
    else:
        bot.send_message(message.chat.id, get_text(user.get("language", "ar"), "welcome"), reply_markup=home_keyboard(user.get("language", "ar"), message.from_user.id in ADMIN_IDS))


@bot.callback_query_handler(func=lambda call: True)
def callback_router(call):
    data = call.data or ""
    user = current_user(call.from_user)
    lang = user.get("language", "ar")
    try:
        bot.answer_callback_query(call.id)
        if data in {"nav_home", "home"}:
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            return show_home(call)
        if data in {"nav_back", "nav_cancel"}:
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            return show_home(call)
        if data == "nav_wallet":
            return render(call, f"💰 <b>{get_text(lang, 'wallet')}</b>\n\nBalance: <code>{float(user['balance']):.2f}</code>", wallet_keyboard(lang))
        if data == "wallet_deposit":
            return prompt_with_cancel(call, "💳 أرسل: المبلغ | طريقة الدفع | رقم العملية\nمثال: 100 | ShamCash | ABC123", receive_deposit)
        if data == "wallet_withdraw":
            return prompt_with_cancel(call, "💸 أرسل: المبلغ | طريقة السحب | معلومات الحساب\nمثال: 100 | MTN | 09XXXXXXXX", receive_withdraw)
        if data == "wallet_transactions":
            conn = get_connection(); rows = conn.execute("SELECT type,amount,balance_after,created_at FROM wallet_transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", (call.from_user.id,)).fetchall(); conn.close()
            text = "📒 <b>آخر العمليات</b>\n\n" + ("\n".join(f"• {r['type']} | {r['amount']} | {r['balance_after']} | {r['created_at']}" for r in rows) if rows else "لا توجد عمليات بعد.")
            return render(call, text, section_keyboard(lang, back="nav_wallet"))
        if data == "nav_games":
            return render(call, get_text(lang, "games"), games_keyboard(lang))
        if data == "nav_lottery":
            round_data = get_active_round()
            if not round_data: return render(call, get_text(lang, "lottery_no_active"), section_keyboard(lang))
            return render(call, f"🎟️ <b>{round_data['title']}</b>\n\nسعر التذكرة: <code>{float(round_data['ticket_price']):.2f}</code>\nالتذاكر: <code>{round_data['tickets_sold']}</code>", lottery_keyboard(lang))
        if data == "lottery_info":
            round_data = get_active_round()
            return render(call, "📊 لا توجد جولة نشطة." if not round_data else f"📊 الجولة: <b>{round_data['title']}</b>\nالتذاكر المباعة: <code>{round_data['tickets_sold']}</code>\nالحالة: <code>{round_data['status']}</code>", section_keyboard(lang, back="nav_lottery"))
        if data == "nav_wheel":
            return render(call, get_text(lang, "wheel"), section_keyboard(lang, [telebot.types.InlineKeyboardButton("🎡 Spin", callback_data="wheel_spin")]))
        if data == "nav_language": return render(call, get_text(lang, "language"), language_keyboard())
        if data in {"set_lang_ar", "set_lang_en"}:
            new_lang = "ar" if data == "set_lang_ar" else "en"; set_user_language(call.from_user.id, new_lang)
            return render(call, get_text(new_lang, "welcome"), home_keyboard(new_lang, call.from_user.id in ADMIN_IDS))
        if data == "nav_profile": return render(call, f"👤 <b>{get_text(lang, 'profile')}</b>\n\n🆔 <code>{user['user_id']}</code>\n💰 <code>{float(user['balance']):.2f}</code>\n📅 {user['created_at']}", section_keyboard(lang))
        if data == "nav_referral": return render(call, f"👥 <b>{get_text(lang, 'referral')}</b>\n\nCode: <code>{user.get('referral_code','')}</code>", section_keyboard(lang))
        if data == "nav_gifts": return render(call, get_text(lang, "gift_code") + "\n\nUse: /redeem CODE", section_keyboard(lang))
        if data == "nav_support": return render(call, get_text(lang, "support"), section_keyboard(lang))
        if data == "nav_my_bots": return render(call, "🤖 <b>بوتاتي</b>\n\nلا توجد بوتات مضافة حاليًا.", section_keyboard(lang))
        if data in {"game_dice", "game_coin"}:
            with get_lock(f"game:{call.from_user.id}"):
                result = play_dice(call.from_user.id, 10) if data == "game_dice" else play_coin(call.from_user.id, 10)
            text = result.get("message", "✅ تمت العملية") if not result.get("ok") else f"✅ النتيجة: <b>{result['result']}</b>\n💰 الجائزة: <code>{result['winnings']:.2f}</code>"
            return render(call, text, games_keyboard(lang))
        if data == "wheel_spin":
            with get_lock(f"wheel:{call.from_user.id}"): result = spin_wheel(call.from_user.id)
            text = result.get("message", "✅ تمت العملية") if not result.get("ok") else f"🎡 النتيجة: <b>{result['result']}</b>\n🎁 المكافأة: <code>{result['reward']:.2f}</code>"
            return render(call, text, section_keyboard(lang, back="nav_wheel"))
        if data == "lottery_buy":
            with get_lock(f"lottery:{call.from_user.id}"): result = buy_ticket(call.from_user.id)
            return render(call, "✅ تم شراء التذكرة" if result.get("ok") else f"❌ {result.get('message')}", lottery_keyboard(lang))
        if data == "admin_panel":
            if call.from_user.id not in ADMIN_IDS: return
            return render(call, "👑 <b>لوحة الإدارة</b>", admin_keyboard())
        if data.startswith("admin_") and call.from_user.id in ADMIN_IDS:
            if data == "admin_backup":
                bot.send_message(call.message.chat.id, "استخدم /backup لإنشاء النسخة وإرسالها.", reply_markup=admin_keyboard()); return
            if data == "admin_pending":
                bot.send_message(call.message.chat.id, "استخدم /pending لعرض الطلبات المعلقة.", reply_markup=admin_keyboard()); return
            stats = get_dashboard_stats()
            return render(call, "📊 <b>لوحة الإدارة</b>\n\n" + "\n".join(f"• {key}: <code>{value}</code>" for key, value in stats.items()), admin_keyboard())
    except Exception:
        logger.exception("Callback failed: %s", data)
        bot.send_message(call.message.chat.id, "❌ حدث خطأ غير متوقع. تم تسجيل المشكلة، حاول مرة أخرى.")


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

register_start(bot); register_user(bot); register_wallet(bot); register_lottery(bot); register_games(bot); register_wheel(bot); register_gifts(bot); register_referral(bot); register_language(bot); register_support(bot); register_admin_operations(bot)

if __name__ == "__main__":
    print(f"🎰 {APP_NAME}\n✅ Database\n✅ Configuration\n🚀 Bot started")
    bot.infinity_polling(timeout=30, long_polling_timeout=30, skip_pending=True)
