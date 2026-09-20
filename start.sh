#!/usr/bin/env bash
set -e

if [ ! -f .env ]; then
  echo "[INFO] .env not found. Copying .env.example to .env"
  cp .env.example .env
fi

python3 -m pip install -r requirements.txt
python3 main.py
