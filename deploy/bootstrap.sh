#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="$HOME/apps/telegram-lead-bot"
SERVICE_DIR="$HOME/.config/systemd/user"

if [[ ! -d "$APP_DIR" ]]; then
  echo "Application directory not found: $APP_DIR"
  exit 1
fi

if [[ ! -f "$APP_DIR/.env" ]]; then
  echo "Create $APP_DIR/.env from .env.example before starting the service."
  exit 1
fi

cd "$APP_DIR"
chmod 600 .env
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

mkdir -p "$SERVICE_DIR"
install -m 644 deploy/telegram-lead-bot.service "$SERVICE_DIR/telegram-lead-bot.service"

systemctl --user daemon-reload
systemctl --user enable --now telegram-lead-bot
systemctl --user status telegram-lead-bot --no-pager
