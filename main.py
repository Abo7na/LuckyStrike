# -*- coding: utf-8 -*-

import os
import sys
import time
import threading

import telebot

from config import BOT_TOKEN, ADMIN_IDS, APP_NAME, TEST_MODE
from database.db import init_db, ensure_user
from handlers.start import register_handlers as register_start_handlers
from handlers.user import register_handlers as register_user_handlers
from handlers.wallet import register_handlers as register_wallet_handlers
from handlers.lottery import register_handlers as register_lottery_handlers
from handlers.games import register_handlers as register_games_handlers
from handlers.wheel import register_handlers as register_wheel_handlers
from handlers.gifts import register_handlers as register_gifts_handlers
from handlers.referral import register_handlers as register_referral_handlers
from handlers.language import register_handlers as register_language_handlers
from handlers.support import register_handlers as register_support_handlers
from handlers.admin.dashboard import register_handlers as register_admin_dashboard_handlers
from handlers.admin.users import register_handlers as register_admin_users_handlers
from handlers.admin.wallet import register_handlers as register_admin_wallet_handlers
from handlers.admin.settings import register_handlers as register_admin_settings_handlers
from handlers.admin.statistics import register_handlers as register_admin_statistics_handlers
from handlers.admin.security import register_handlers as register_admin_security_handlers
from utils.helpers import get_text


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Please fill .env")

init_db()

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')


def safe_text(lang, key):
    return get_text(lang, key)


@bot.message_handler(commands=['help'])
def help_command(message):
    user = ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    lang = user.get('language', 'ar')
    bot.send_message(message.chat.id, safe_text(lang, 'welcome'))


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data or ''
    if data == 'nav_wallet':
        bot.send_message(call.message.chat.id, 'Wallet menu')
    elif data == 'nav_language':
        bot.send_message(call.message.chat.id, 'Language menu')
    elif data == 'home':
        user = ensure_user(call.from_user.id, call.from_user.username, call.from_user.first_name, call.from_user.last_name)
        bot.send_message(call.message.chat.id, safe_text(user.get('language', 'ar'), 'welcome'))
    elif data == 'admin_users':
        if call.from_user.id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, 'Access denied')
            return
        bot.send_message(call.message.chat.id, 'Admin user operations')
    elif data == 'admin_wallet':
        if call.from_user.id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, 'Access denied')
            return
        bot.send_message(call.message.chat.id, 'Wallet management panel')
    elif data == 'admin_lottery':
        if call.from_user.id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, 'Access denied')
            return
        bot.send_message(call.message.chat.id, 'Lottery management panel')
    elif data == 'admin_stats':
        if call.from_user.id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, 'Access denied')
            return
        bot.send_message(call.message.chat.id, 'Statistics panel')
    else:
        bot.answer_callback_query(call.id, 'Action processed')


register_start_handlers(bot)
register_user_handlers(bot)
register_wallet_handlers(bot)
register_lottery_handlers(bot)
register_games_handlers(bot)
register_wheel_handlers(bot)
register_gifts_handlers(bot)
register_referral_handlers(bot)
register_language_handlers(bot)
register_support_handlers(bot)
register_admin_dashboard_handlers(bot)
register_admin_users_handlers(bot)
register_admin_wallet_handlers(bot)
register_admin_settings_handlers(bot)
register_admin_statistics_handlers(bot)
register_admin_security_handlers(bot)


if __name__ == '__main__':
    print(f"[START] {APP_NAME} bot is running...")
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
