from config import ADMIN_IDS
from database.db import get_connection, log_admin_action
from utils.backup import create_database_backup


def register_handlers(bot):
    @bot.message_handler(commands=["backup"])
    def backup_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        try:
            path = create_database_backup()
            log_admin_action(message.from_user.id, "database_backup", details=path.name)
            with open(path, "rb") as document:
                bot.send_document(message.chat.id, document, caption="✅ Database backup created")
        except Exception:
            bot.send_message(message.chat.id, "❌ Backup failed. Check the server logs.")

    @bot.message_handler(commands=["pending"])
    def pending_cmd(message):
        if message.from_user.id not in ADMIN_IDS:
            return
        conn = get_connection()
        rows = conn.execute("SELECT request_id,user_id,kind,amount,method,created_at FROM wallet_requests WHERE status='PENDING' ORDER BY id LIMIT 30").fetchall()
        conn.close()
        if not rows:
            bot.send_message(message.chat.id, "✅ No pending wallet requests.")
            return
        text = "📥 <b>Pending requests</b>\n\n" + "\n".join(f"<code>{r['request_id']}</code> | {r['kind']} | {r['amount']} | user {r['user_id']}\n/approve {r['request_id']}   /reject {r['request_id']}" for r in rows)
        bot.send_message(message.chat.id, text)
