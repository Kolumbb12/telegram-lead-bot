import logging
import re
from html import escape

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from .database import Database
from .keyboards import confirmation_menu, language_menu, main_menu, phone_keyboard, service_menu
from .localization import SERVICES, all_button_values, service_name, text
from .states import LeadForm

logger = logging.getLogger(__name__)
router = Router()
MAX_LEAD_PREVIEW_LENGTH = 500
MAX_MESSAGE_LENGTH = 3800


def is_admin(message: Message, admin_ids: tuple[int, ...]) -> bool:
    return bool(message.from_user and message.from_user.id in admin_ids)


def valid_phone(value: str) -> bool:
    return bool(re.fullmatch(r"\+?[\d\s().-]+", value)) and 10 <= len(re.sub(r"\D", "", value)) <= 15


def normalize_phone(value: str) -> str:
    """Store a consistent, human-readable phone value after validation."""
    digits = re.sub(r"\D", "", value)
    return f"+{digits}" if value.lstrip().startswith("+") else digits


def escaped_preview(value: str, limit: int) -> str:
    """Escape and truncate content without cutting an HTML entity in half."""
    parts: list[str] = []
    length = 0
    for character in value:
        encoded = escape(character)
        if length + len(encoded) > limit:
            return "".join(parts) + "…"
        parts.append(encoded)
        length += len(encoded)
    return "".join(parts)


def format_created_at(value: str) -> str:
    return value[:16].replace("T", " ") + " UTC"


async def form_language(state: FSMContext, database: Database, user_id: int) -> str:
    data = await state.get_data()
    return str(data.get("language") or await database.get_language(user_id))


async def send_lead_list(message: Message, language: str, rows: list[dict[str, object]]) -> None:
    """Split the lead list into Telegram-safe HTML messages when needed."""
    header = text(language, "latest_leads")
    current = header
    for row in rows:
        block = (
            f"\n\n<b>#{row['id']} · {escape(format_created_at(str(row['created_at'])))}</b>"
            f"\n{escaped_preview(str(row['name']), 200)} — {escape(service_name(str(row['service']), language))}"
            f"\n{text(language, 'phone_label')}: {escaped_preview(str(row['phone']), 100)}"
            f"\n{escaped_preview(str(row['comment']), MAX_LEAD_PREVIEW_LENGTH)}"
        )
        if len(current) + len(block) > MAX_MESSAGE_LENGTH and current != header:
            await message.answer(current, parse_mode="HTML")
            current = header
        current += block
    await message.answer(current, parse_mode="HTML")


async def begin_lead(message: Message, state: FSMContext, database: Database) -> None:
    language = await database.get_language(message.from_user.id)
    await state.clear()
    await state.update_data(language=language)
    await state.set_state(LeadForm.service)
    await message.answer(text(language, "choose_service"), reply_markup=service_menu(language))


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, database: Database) -> None:
    language = await database.get_language(message.from_user.id)
    await state.clear()
    await message.answer(text(language, "welcome"), reply_markup=main_menu(language))


@router.message(Command("help"))
async def help_command(message: Message, database: Database) -> None:
    language = await database.get_language(message.from_user.id)
    await message.answer(text(language, "help"), reply_markup=main_menu(language))


@router.message(Command("language"))
@router.message(F.text.in_(all_button_values("language")))
async def choose_language(message: Message) -> None:
    await message.answer("Choose your language / Выберите язык:", reply_markup=language_menu())


@router.callback_query(F.data.in_({"language:en", "language:ru"}))
async def save_language(callback: CallbackQuery, state: FSMContext, database: Database) -> None:
    language = callback.data.rsplit(":", 1)[1]
    await database.set_language(callback.from_user.id, language)
    await state.clear()
    await callback.answer()
    await callback.message.answer(text(language, "language_saved"), reply_markup=main_menu(language))


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext, database: Database) -> None:
    language = await form_language(state, database, message.from_user.id)
    await state.clear()
    await message.answer(text(language, "cancelled"), reply_markup=main_menu(language))


@router.message(Command("leads"))
async def leads(message: Message, database: Database, admin_ids: tuple[int, ...]) -> None:
    if not is_admin(message, admin_ids):
        return
    language = await database.get_language(message.from_user.id)
    rows = await database.get_latest()
    if not rows:
        await message.answer(text(language, "no_leads"))
        return

    await send_lead_list(message, language, rows)


@router.message(Command("stats"))
async def stats(message: Message, database: Database, admin_ids: tuple[int, ...]) -> None:
    if not is_admin(message, admin_ids):
        return
    language = await database.get_language(message.from_user.id)
    total, services = await database.get_stats()
    details = "\n".join(
        f"• {escape(service_name(service, language))}: {count}" for service, count in services
    ) or text(language, "no_service_data")
    await message.answer(text(language, "statistics", total=total, details=details), parse_mode="HTML")


@router.message(F.text.in_(all_button_values("lead")))
async def start_lead(message: Message, state: FSMContext, database: Database) -> None:
    await begin_lead(message, state, database)


@router.message(F.text.in_(all_button_values("about")))
async def about(message: Message, database: Database) -> None:
    language = await database.get_language(message.from_user.id)
    await message.answer(text(language, "about"), reply_markup=main_menu(language))


@router.callback_query(LeadForm.service, F.data.startswith("service:"))
async def choose_service(callback: CallbackQuery, state: FSMContext, database: Database) -> None:
    service = callback.data.split(":", 1)[1]
    language = await form_language(state, database, callback.from_user.id)
    if service not in SERVICES["en"]:
        await callback.answer(text(language, "stale_option"), show_alert=True)
        return
    await state.update_data(service=service)
    await state.set_state(LeadForm.name)
    await callback.answer()
    await callback.message.answer(text(language, "ask_name"))


@router.message(LeadForm.name, F.text)
async def get_name(message: Message, state: FSMContext, database: Database) -> None:
    language = await form_language(state, database, message.from_user.id)
    name = message.text.strip()
    if not 2 <= len(name) <= 100:
        await message.answer(text(language, "invalid_name"))
        return
    await state.update_data(name=name)
    await state.set_state(LeadForm.phone)
    await message.answer(text(language, "ask_phone"), reply_markup=phone_keyboard(language))


@router.message(LeadForm.phone, F.contact)
async def get_contact(message: Message, state: FSMContext, database: Database) -> None:
    language = await form_language(state, database, message.from_user.id)
    if message.contact.user_id and message.contact.user_id != message.from_user.id:
        await message.answer(text(language, "foreign_contact"))
        return
    await save_phone(message, state, language, message.contact.phone_number)


@router.message(LeadForm.phone, F.text)
async def get_phone(message: Message, state: FSMContext, database: Database) -> None:
    language = await form_language(state, database, message.from_user.id)
    await save_phone(message, state, language, message.text.strip())


async def save_phone(message: Message, state: FSMContext, language: str, phone: str) -> None:
    if not valid_phone(phone):
        await message.answer(text(language, "invalid_phone"))
        return
    await state.update_data(phone=normalize_phone(phone))
    await state.set_state(LeadForm.comment)
    await message.answer(text(language, "ask_comment"), reply_markup=ReplyKeyboardRemove())


@router.message(LeadForm.comment, F.text)
async def get_comment(message: Message, state: FSMContext, database: Database) -> None:
    language = await form_language(state, database, message.from_user.id)
    comment = message.text.strip()
    if not 3 <= len(comment) <= 2000:
        await message.answer(text(language, "invalid_comment"))
        return
    await state.update_data(comment=comment)
    data = await state.get_data()
    await state.set_state(LeadForm.confirmation)
    await message.answer(
        text(
            language,
            "lead_summary",
            name=escaped_preview(data["name"], 300),
            service=escape(service_name(data["service"], language)),
            phone=escaped_preview(data["phone"], 100),
            comment=escaped_preview(data["comment"], 2500),
        ),
        reply_markup=confirmation_menu(language),
        parse_mode="HTML",
    )


@router.callback_query(LeadForm.confirmation, F.data == "lead:restart")
async def restart(callback: CallbackQuery, state: FSMContext, database: Database) -> None:
    await callback.answer()
    await begin_lead(callback.message, state, database)


@router.callback_query(LeadForm.confirmation, F.data == "lead:cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext, database: Database) -> None:
    language = await form_language(state, database, callback.from_user.id)
    await state.clear()
    await callback.answer(text(language, "lead_cancelled"))
    await callback.message.answer(text(language, "lead_cancelled"), reply_markup=main_menu(language))


@router.callback_query(LeadForm.confirmation, F.data == "lead:submit")
async def submit(callback: CallbackQuery, state: FSMContext, database: Database, admin_ids: tuple[int, ...]) -> None:
    language = await form_language(state, database, callback.from_user.id)
    data = await state.get_data()
    user = callback.from_user
    try:
        lead_id, created_at = await database.create_lead(
            {
                "telegram_user_id": user.id,
                "telegram_username": user.username,
                "name": data["name"],
                "service": data["service"],
                "phone": data["phone"],
                "comment": data["comment"],
            }
        )
    except Exception:
        logger.exception("Could not save lead from user %s", user.id)
        await callback.answer(text(language, "lead_submit_failed"), show_alert=True)
        return

    await state.clear()
    await callback.answer(text(language, "lead_sent"))
    await callback.message.answer(text(language, "lead_sent"), reply_markup=main_menu(language))

    for admin_id in admin_ids:
        admin_language = await database.get_language(admin_id)
        username = f"@{user.username}" if user.username else text(admin_language, "unknown_username")
        notification = text(
            admin_language,
            "admin_lead",
            lead_id=lead_id,
            name=escaped_preview(data["name"], 300),
            username=escape(username),
            user_id=user.id,
            service=escape(service_name(data["service"], admin_language)),
            phone=escaped_preview(data["phone"], 100),
            comment=escaped_preview(data["comment"], 2500),
            created_at=escape(format_created_at(created_at)),
        )
        try:
            await callback.bot.send_message(admin_id, notification, parse_mode="HTML")
        except Exception:
            logger.exception("Could not notify administrator about lead #%s", lead_id)
