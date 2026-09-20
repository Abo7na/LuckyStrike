# Lucky Strike

A modular Telegram bot for Termux/Linux/Windows with an Arabic/English inline two-column interface.

## Included flows
- Modern inline navigation with home/back controls.
- SQLite WAL mode, foreign keys, constraints, indexes and migrations.
- Atomic wallet ledger operations.
- Manual deposit flow: `amount | method | payment_reference`.
- Manual withdrawal flow: `amount | method | account_details`; funds are held atomically and refunded on rejection.
- Admin pending review: `/pending`, `/approve REQUEST_ID`, `/reject REQUEST_ID`.
- Lottery tickets selected by ticket ID, not distinct users.
- Dice, coin and server-time wheel cooldown.
- Atomic, expiry-aware and per-user gift redemption.
- WAL-safe SQLite backup with `/backup`.

## Install
```bash
pkg update
pkg install python git
python -m pip install -r requirements.txt
cp .env.example .env
```
Set `BOT_TOKEN` and numeric Telegram IDs in `ADMIN_IDS`, then run:
```bash
python main.py
```

## Test before production
```bash
TEST_MODE=true python -m unittest discover -s tests -v
python -m compileall -q .
```

## Admin commands
```text
/admin   /panel
/stats
/pending
/approve REQUEST_ID
/reject REQUEST_ID
/backup
```

No payment API is assumed. The administrator must verify payment references manually before approving deposits. Never commit `.env`, tokens, or production database files.
