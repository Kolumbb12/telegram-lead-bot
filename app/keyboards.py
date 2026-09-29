from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .localization import SERVICES, button, normalize_language


def main_menu(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=button(language, "lead"))],
            [KeyboardButton(text=button(language, "language")), KeyboardButton(text=button(language, "about"))],
        ],
        resize_keyboard=True,
    )


def service_menu(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, title in SERVICES[normalize_language(language)].items():
        builder.button(text=title, callback_data=f"service:{key}")
    builder.adjust(2)
    return builder.as_markup()


def phone_keyboard(language: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button(language, "share_phone"), request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def confirmation_menu(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=button(language, "submit"), callback_data="lead:submit")
    builder.button(text=button(language, "restart"), callback_data="lead:restart")
    builder.button(text=button(language, "cancel"), callback_data="lead:cancel")
    builder.adjust(1)
    return builder.as_markup()


def language_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="English", callback_data="language:en")
    builder.button(text="Русский", callback_data="language:ru")
    builder.adjust(2)
    return builder.as_markup()
