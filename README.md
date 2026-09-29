# Telegram Lead Bot

Демонстрационный Telegram-бот для сбора заявок клиентов и мгновенного уведомления администратора. Компактный production-like проект для портфолио фрилансера.

## Возможности

- пошаговая форма заявки через FSM;
- выбор услуги, имени, телефона и комментария;
- сохранение заявок в SQLite;
- уведомления администратора;
- несколько администраторов через один параметр окружения;
- базовая валидация телефона и защита пользовательского текста в HTML-сообщениях;
- команды `/leads`, `/stats`, `/help` и `/cancel`.

## Стек

Python 3.12+, aiogram 3, SQLite, aiosqlite, python-dotenv.

## Структура

```text
app/
  bot.py          # запуск приложения
  config.py       # настройки из .env
  database.py     # SQLite
  handlers.py     # команды и форма заявки
  keyboards.py    # клавиатуры
  states.py       # состояния FSM
```

## Установка и запуск

1. Клонируйте репозиторий, создайте виртуальное окружение и установите зависимости:

   ```bash
   git clone https://github.com/Kolumbb12/telegram-lead-bot.git
   cd telegram-lead-bot
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Скопируйте `.env.example` в `.env` и заполните `BOT_TOKEN` и `ADMIN_ID`.
3. Запустите бота:

   ```bash
   python -m app.bot
   ```

База `leads.db` и таблицы создаются автоматически при первом запуске. Если администраторов несколько, укажите их ID через запятую в `ADMIN_ID`, например `123456789,987654321`.

`.env` и база данных исключены из Git. Не публикуйте токен бота или содержимое базы данных.

## Настройка Telegram

Получите `BOT_TOKEN` у [@BotFather](https://t.me/BotFather): создайте бота командой `/newbot` и скопируйте выданный токен.

Чтобы узнать Telegram ID администратора, можно написать боту [@userinfobot](https://t.me/userinfobot) и указать полученный ID в `ADMIN_ID`.

## Административные команды

Команды `/leads` и `/stats` доступны только пользователю, чей ID указан в `ADMIN_ID`.
