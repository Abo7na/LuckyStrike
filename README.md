# Lucky Strike

Lucky Strike is a modular Telegram bot project designed for Android/Termux compatibility and easy later migration to Linux/VPS/Windows.

## Features
- User dashboard
- Wallet system with ledger
- Manual deposit and withdrawal approval flow
- Lottery system
- Game engine (dice, coin, wheel)
- Gift code support
- Referral system
- Language switcher (Arabic/English)
- Support section
- Admin dashboard and permission system
- Security checks and anti-spam protections
- SQLite with WAL mode and transactions

## Structure
```text
LuckyStrike/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── start.sh
├── database/
├── handlers/
├── services/
├── keyboards/
├── utils/
├── locales/
├── data/
├── backups/
├── logs/
└── .env
```

## Setup
1. Install Python 3.11+
2. On Android/Termux:
   ```bash
   pkg update
   pkg install python git
   git clone https://github.com/Abo7na/LuckyStrike.git
   cd LuckyStrike
   cp .env.example .env
   ```
3. Set your Telegram bot token in `.env`.
4. Start:
   ```bash
   bash start.sh
   ```

## .env
```env
BOT_TOKEN=your_telegram_token_here
ADMIN_IDS=123456789
DATABASE_PATH=data/luckystrike.db
TEST_MODE=false
```

## Notes
- Payment APIs are intentionally not included because no payment provider credentials were provided.
- Deposit and withdrawal flows are handled manually through admin approval.
- The project is built to be modular and extendable.
