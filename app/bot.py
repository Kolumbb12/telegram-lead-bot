import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .config import load_config
from .database import Database
from .handlers import router


async def main() -> None:
    """Initialize application dependencies and start long polling."""
    config = load_config()
    database = Database(config.database_path)
    await database.initialize()
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Open the main menu"),
            BotCommand(command="help", description="Show help"),
            BotCommand(command="language", description="Change language"),
            BotCommand(command="cancel", description="Cancel a lead"),
        ],
        language_code="en",
    )
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Открыть главное меню"),
            BotCommand(command="help", description="Показать справку"),
            BotCommand(command="language", description="Сменить язык"),
            BotCommand(command="cancel", description="Отменить заявку"),
        ],
        language_code="ru",
    )
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router)
    dispatcher["database"] = database
    dispatcher["admin_ids"] = config.admin_ids
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    try:
        asyncio.run(main())
    except ValueError as error:
        logging.error("Ошибка конфигурации: %s", error)
        raise SystemExit(1) from error
