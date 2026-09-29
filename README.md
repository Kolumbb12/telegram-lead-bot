# Telegram Lead Bot

![CI](https://github.com/Kolumbb12/telegram-lead-bot/actions/workflows/ci.yml/badge.svg)

## English

A portfolio-ready Telegram bot for collecting client leads and sending instant notifications to administrators.

### Features

- English interface by default, with a full Russian translation;
- language selector with a saved user preference;
- guided lead form: service, name, phone number and project description;
- Telegram contact-sharing button and manual phone validation;
- confirmation screen with submit, restart and cancel actions;
- SQLite storage created automatically on first launch;
- notifications for one or more administrators;
- protected `/leads` and `/stats` commands;
- `/start`, `/help`, `/language` and `/cancel` commands;
- safe HTML rendering, message-length handling and application logging.

### Stack

Python 3.12+, aiogram 3, SQLite, aiosqlite and python-dotenv.

### Project structure

```text
app/
  bot.py           # application entry point
  config.py        # environment configuration
  database.py      # SQLite repository
  handlers.py      # commands and lead flow
  keyboards.py     # Telegram keyboards
  localization.py  # English and Russian interface text
  states.py        # FSM states
tests/             # automated tests
```

### Installation and launch

```bash
git clone https://github.com/Kolumbb12/telegram-lead-bot.git
cd telegram-lead-bot
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set the values:

```env
BOT_TOKEN=your_token_from_botfather
ADMIN_ID=123456789,987654321
```

`ADMIN_ID` accepts one or more Telegram IDs separated by commas. Run the bot:

```bash
python -m app.bot
```

The SQLite database and required tables are created automatically. `.env` and local database files are excluded from Git.

### Telegram setup

Create a bot with [@BotFather](https://t.me/BotFather) using `/newbot`, then copy the token into `.env`.

To find an administrator's Telegram ID, use [@userinfobot](https://t.me/userinfobot). Administrators can use:

- `/leads` — show the ten latest leads;
- `/stats` — show total leads and service breakdown.

### Quality checks

The project has pytest coverage for database operations, localization, keyboards and input validation. GitHub Actions runs compilation and tests on every push and pull request to `main`.

```bash
pip install -r requirements-dev.txt
pytest -q
```

### Continuous deployment to Oracle Cloud Always Free

This repository includes a CD workflow for an Oracle Cloud Always Free VM. It keeps the polling bot running through a systemd user service and deploys each push to `main` after the following one-time setup:

1. Create an Ubuntu VM in the Oracle Cloud Always Free tier and allow SSH access only from trusted IP addresses.
2. SSH into the VM, clone this repository to `~/apps/telegram-lead-bot`, create `.env` from `.env.example`, add the production values, then run `deploy/bootstrap.sh`.
3. Run `sudo loginctl enable-linger $USER` once on the VM so the user service remains active after logout.
4. Add these GitHub Actions repository secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` and `DEPLOY_KNOWN_HOSTS`.

Use `ssh-keyscan -H YOUR_SERVER_IP` from a trusted machine to obtain the value for `DEPLOY_KNOWN_HOSTS`. The workflow syncs source code but deliberately excludes `.env`, SQLite files and virtual environments. The deploy job stays skipped until all four secrets are configured.

---

## Русский

Готовый Telegram-бот для портфолио, который собирает заявки клиентов и мгновенно уведомляет администраторов.

### Возможности

- английский интерфейс по умолчанию и полная русская локализация;
- выбор языка с сохранением настройки пользователя;
- пошаговая заявка: услуга, имя, номер телефона и описание задачи;
- кнопка отправки контакта Telegram и ручная проверка номера;
- экран подтверждения с отправкой, перезаполнением и отменой;
- автоматическое создание SQLite-базы при первом запуске;
- уведомления для одного или нескольких администраторов;
- защищённые команды `/leads` и `/stats`;
- команды `/start`, `/help`, `/language` и `/cancel`;
- безопасный HTML-вывод, учёт лимитов сообщений и логирование.

### Стек

Python 3.12+, aiogram 3, SQLite, aiosqlite и python-dotenv.

### Структура проекта

```text
app/
  bot.py           # точка входа приложения
  config.py        # конфигурация из окружения
  database.py      # работа с SQLite
  handlers.py      # команды и сценарий заявки
  keyboards.py     # клавиатуры Telegram
  localization.py  # тексты на английском и русском
  states.py        # состояния FSM
tests/             # автоматические тесты
```

### Установка и запуск

```bash
git clone https://github.com/Kolumbb12/telegram-lead-bot.git
cd telegram-lead-bot
python -m venv .venv
```

Активируйте окружение и установите зависимости:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Скопируйте `.env.example` в `.env` и укажите значения:

```env
BOT_TOKEN=your_token_from_botfather
ADMIN_ID=123456789,987654321
```

В `ADMIN_ID` можно указать один или несколько Telegram ID через запятую. Запустите бота:

```bash
python -m app.bot
```

SQLite-база и нужные таблицы создаются автоматически. `.env` и локальные файлы базы данных исключены из Git.

### Настройка Telegram

Создайте бота у [@BotFather](https://t.me/BotFather) командой `/newbot`, затем скопируйте токен в `.env`.

Чтобы узнать Telegram ID администратора, воспользуйтесь [@userinfobot](https://t.me/userinfobot). Администраторам доступны:

- `/leads` — десять последних заявок;
- `/stats` — общее количество и разбивка по услугам.

### Проверки качества

Проект содержит pytest-тесты для базы данных, локализации, клавиатур и валидации ввода. GitHub Actions запускает компиляцию и тесты при каждом push и pull request в `main`.

```bash
pip install -r requirements-dev.txt
pytest -q
```

### Continuous deployment в Oracle Cloud Always Free

В репозитории есть CD-пайплайн для VM Oracle Cloud Always Free. Бот работает как systemd user service, а каждый push в `main` разворачивает новую версию после однократной настройки:

1. Создайте Ubuntu VM в Oracle Cloud Always Free и разрешите SSH только с доверенных IP-адресов.
2. Подключитесь к VM по SSH, склонируйте репозиторий в `~/apps/telegram-lead-bot`, создайте `.env` из `.env.example`, добавьте production-значения и запустите `deploy/bootstrap.sh`.
3. Один раз выполните на VM `sudo loginctl enable-linger $USER`, чтобы user service работал после выхода из SSH.
4. Добавьте в GitHub Actions repository secrets: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY` и `DEPLOY_KNOWN_HOSTS`.

Получите значение `DEPLOY_KNOWN_HOSTS` на доверенной машине командой `ssh-keyscan -H YOUR_SERVER_IP`. Пайплайн синхронизирует исходники, но намеренно исключает `.env`, SQLite-файлы и виртуальное окружение. Пока не настроены все четыре секрета, deploy job будет пропущен.
