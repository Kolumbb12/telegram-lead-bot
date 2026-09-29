from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 Оставить заявку")], [KeyboardButton(text="ℹ️ О боте")]],
        resize_keyboard=True,
    )


def service_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, title in (("bot", "Telegram-бот"), ("automation", "Автоматизация"),
                       ("parsing", "Парсинг данных"), ("other", "Другое")):
        builder.button(text=title, callback_data=f"service:{key}")
    builder.adjust(2)
    return builder.as_markup()


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def confirmation_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Отправить", callback_data="lead:submit")
    builder.button(text="✏️ Заполнить заново", callback_data="lead:restart")
    builder.button(text="❌ Отмена", callback_data="lead:cancel")
    builder.adjust(1)
    return builder.as_markup()
