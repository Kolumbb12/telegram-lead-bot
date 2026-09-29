from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: tuple[int, ...]
    database_path: str = "leads.db"


def load_config() -> Config:
    """Load and validate required settings without ever logging their values."""
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    admin_value = os.getenv("ADMIN_ID", "").strip()
    if not token:
        raise ValueError("BOT_TOKEN не задан в файле .env")
    if not admin_value:
        raise ValueError("ADMIN_ID не задан в файле .env")
    try:
        admin_ids = tuple(int(value.strip()) for value in admin_value.split(",") if value.strip())
    except ValueError as exc:
        raise ValueError("ADMIN_ID должен содержать числовые ID через запятую") from exc
    if not admin_ids or any(admin_id <= 0 for admin_id in admin_ids):
        raise ValueError("ADMIN_ID должен содержать хотя бы один ID")
    return Config(bot_token=token, admin_ids=tuple(dict.fromkeys(admin_ids)))
