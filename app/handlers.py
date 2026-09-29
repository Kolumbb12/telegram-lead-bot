import logging
import re
from html import escape

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from .database import Database
from .keyboards import confirmation_menu, main_menu, phone_keyboard, service_menu
from .states import LeadForm

logger = logging.getLogger(__name__)
router = Router()
SERVICE_NAMES = {
    "bot": "Telegram-бот",
    "automation": "Автоматизация",
    "parsing": "Парсинг данных",
    "other": "Другое",
}
MAX_LEAD_PREVIEW_LENGTH = 500


def is_admin(message: Message, admin_ids: tuple[int, ...]) -> bool:
    return bool(message.from_user and message.from_user.id in admin_ids)


def valid_phone(value: str) -> bool:
    return bool(re.fullmatch(r"\+?[\d\s().-]+", value)) and 10 <= len(re.sub(r"\D", "", value)) <= 15


def normalize_phone(value: str) -> str:
    """Store a consistent, human-readable phone value after validation."""
    digits = re.sub(r"\D", "", value)
    return f"+{digits}" if value.lstrip().startswith("+") else digits


def lead_preview(comment: str) -> str:
    """Keep admin list messages safely under Telegram's message length limit."""
    return comment if len(comment) <= MAX_LEAD_PREVIEW_LENGTH else f"{comment[:MAX_LEAD_PREVIEW_LENGTH - 1]}…"


def format_created_at(value: str) -> str:
    """Present stored UTC timestamps in a compact readable form."""
    return value[:16].replace("T", " ") + " UTC"


async def begin_lead(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LeadForm.service)
    await message.answer("Выберите услугу:", reply_markup=service_menu())


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Здравствуйте! Я помогу оставить заявку на разработку или автоматизацию.", reply_markup=main_menu())


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer("Чтобы оставить заявку, нажмите «📝 Оставить заявку» и последовательно заполните форму. Для отмены используйте /cancel.", reply_markup=main_menu())


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Заполнение заявки отменено.", reply_markup=main_menu())


@router.message(Command("leads"))
async def leads(message: Message, database: Database, admin_ids: tuple[int, ...]) -> None:
    if not is_admin(message, admin_ids):
        return
    rows = await database.get_latest()
    if not rows:
        await message.answer("Заявок пока нет.")
        return

    lines = ["<b>Последние заявки:</b>"]
    for row in rows:
        lines.append(
            f"\n<b>#{row['id']} · {escape(format_created_at(row['created_at']))}</b>"
            f"\n{escape(row['name'])} — {escape(row['service'])}"
            f"\nТелефон: {escape(row['phone'])}"
            f"\n{escape(lead_preview(row['comment']))}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("stats"))
async def stats(message: Message, database: Database, admin_ids: tuple[int, ...]) -> None:
    if not is_admin(message, admin_ids):
        return
    total, services = await database.get_stats()
    details = "\n".join(f"• {escape(service)}: {count}" for service, count in services) or "Нет данных по услугам"
    await message.answer(f"<b>Статистика заявок</b>\n\nВсего: {total}\n\n{details}", parse_mode="HTML")


@router.message(F.text == "📝 Оставить заявку")
async def start_lead(message: Message, state: FSMContext) -> None:
    await begin_lead(message, state)


@router.message(F.text == "ℹ️ О боте")
async def about(message: Message) -> None:
    await message.answer("Этот бот собирает заявки и передаёт их администратору. /help — справка.", reply_markup=main_menu())


@router.callback_query(LeadForm.service, F.data.startswith("service:"))
async def choose_service(callback: CallbackQuery, state: FSMContext) -> None:
    key = callback.data.split(":", 1)[1]
    await state.update_data(service=SERVICE_NAMES.get(key, "Другое"))
    await state.set_state(LeadForm.name)
    await callback.answer()
    await callback.message.answer("Как вас зовут?")


@router.message(LeadForm.name, F.text)
async def get_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not 2 <= len(name) <= 100:
        await message.answer("Введите имя длиной от 2 до 100 символов.")
        return
    await state.update_data(name=name)
    await state.set_state(LeadForm.phone)
    await message.answer("Укажите номер телефона или воспользуйтесь кнопкой ниже:", reply_markup=phone_keyboard())


@router.message(LeadForm.phone, F.contact)
async def get_contact(message: Message, state: FSMContext) -> None:
    if message.contact.user_id and message.contact.user_id != message.from_user.id:
        await message.answer("Отправьте свой контакт или введите номер вручную.")
        return
    await save_phone(message, state, message.contact.phone_number)


@router.message(LeadForm.phone, F.text)
async def get_phone(message: Message, state: FSMContext) -> None:
    await save_phone(message, state, message.text.strip())


async def save_phone(message: Message, state: FSMContext, phone: str) -> None:
    if not valid_phone(phone):
        await message.answer("Не удалось распознать номер. Введите номер длиной от 10 до 15 цифр.")
        return
    await state.update_data(phone=normalize_phone(phone))
    await state.set_state(LeadForm.comment)
    await message.answer("Кратко опишите вашу задачу:", reply_markup=ReplyKeyboardRemove())


@router.message(LeadForm.comment, F.text)
async def get_comment(message: Message, state: FSMContext) -> None:
    comment = message.text.strip()
    if not 3 <= len(comment) <= 2000:
        await message.answer("Описание должно содержать от 3 до 2000 символов.")
        return
    await state.update_data(comment=comment)
    data = await state.get_data()
    await state.set_state(LeadForm.confirmation)
    await message.answer(
        f"<b>Новая заявка</b>\n\nИмя: {escape(data['name'])}\nУслуга: {escape(data['service'])}\nТелефон: {escape(data['phone'])}\nКомментарий: {escape(data['comment'])}",
        reply_markup=confirmation_menu(), parse_mode="HTML",
    )


@router.callback_query(LeadForm.confirmation, F.data == "lead:restart")
async def restart(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await begin_lead(callback.message, state)


@router.callback_query(LeadForm.confirmation, F.data == "lead:cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Заявка отменена")
    await callback.message.answer("Заявка отменена.", reply_markup=main_menu())


@router.callback_query(LeadForm.confirmation, F.data == "lead:submit")
async def submit(callback: CallbackQuery, state: FSMContext, database: Database, admin_ids: tuple[int, ...]) -> None:
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
        logger.exception("Не удалось сохранить заявку пользователя %s", user.id)
        await callback.answer("Не удалось отправить заявку", show_alert=True)
        return

    await state.clear()
    await callback.answer("Заявка отправлена")
    await callback.message.answer("✅ Заявка отправлена.\nСпасибо! С вами свяжутся после рассмотрения заявки.", reply_markup=main_menu())
    username = f"@{user.username}" if user.username else "не указан"
    notification = (
        f"📩 <b>Новая заявка #{lead_id}</b>\n\n"
        f"Имя: {escape(data['name'])}\n"
        f"Telegram: {escape(username)} (ID: {user.id})\n"
        f"Услуга: {escape(data['service'])}\n"
        f"Телефон: {escape(data['phone'])}\n"
        f"Комментарий: {escape(data['comment'])}\n"
        f"Дата создания: {format_created_at(created_at)}"
    )
    for admin_id in admin_ids:
        try:
            await callback.bot.send_message(admin_id, notification, parse_mode="HTML")
        except Exception:
            logger.exception("Не удалось отправить уведомление администратору о заявке #%s", lead_id)
