# Lucky Strike

A modular Telegram entertainment bot for Termux/Linux/Windows with an Arabic/English inline two-column UI.

## Current implemented flows
- Central inline navigation with home/back controls.
- SQLite WAL database with foreign keys, constraints and migrations for the current schema.
- Atomic wallet ledger operations and idempotent request decisions.
- Manual deposit requests and held withdrawals; admin approval/rejection commands.
- Lottery tickets selected by ticket ID, not distinct users.
- Dice, coin and server-time wheel cooldown.
- Atomic, expiry-aware, per-user gift redemption.
- Admin database backup and pending request listing.

## Install
```bash
pkg update
pkg install python git
python -m pip install -r requirements.txt
cp .env.example .env
```
Set `BOT_TOKEN` and the numeric Telegram IDs in `ADMIN_IDS`, then run:
```bash
python main.py
```

## Admin commands
```text
/admin or /panel
/stats
/pending
/approve REQUEST_ID
/reject REQUEST_ID
/backup
```

## Manual payment model
No payment API is required. An administrator must verify a payment reference before approving a deposit. A withdrawal is held atomically and returned through a ledger refund if rejected.

## Safety
Use `TEST_MODE=true` while testing. Never commit `.env`, tokens, payment credentials, or production database files. This project must be tested with a separate Telegram bot before handling real balances.
