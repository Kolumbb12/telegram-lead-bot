from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite


class Database:
    """Small async repository for lead data stored in a local SQLite file."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)

    async def initialize(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            # WAL allows short reads while another request writes a lead.
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA busy_timeout=5000")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_user_id INTEGER NOT NULL,
                    telegram_username TEXT,
                    name TEXT NOT NULL,
                    service TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    telegram_user_id INTEGER PRIMARY KEY,
                    language TEXT NOT NULL CHECK (language IN ('en', 'ru'))
                )
            """)
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC)"
            )
            await db.commit()

    async def get_language(self, telegram_user_id: int) -> str:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA busy_timeout=5000")
            cursor = await db.execute(
                "SELECT language FROM user_settings WHERE telegram_user_id = ?",
                (telegram_user_id,),
            )
            row = await cursor.fetchone()
            return str(row[0]) if row else "en"

    async def set_language(self, telegram_user_id: int, language: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA busy_timeout=5000")
            await db.execute(
                """INSERT INTO user_settings (telegram_user_id, language)
                VALUES (?, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET language = excluded.language""",
                (telegram_user_id, language),
            )
            await db.commit()

    async def create_lead(self, data: dict[str, Any]) -> tuple[int, str]:
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA busy_timeout=5000")
            cursor = await db.execute(
                """INSERT INTO leads
                (telegram_user_id, telegram_username, name, service, phone, comment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data["telegram_user_id"], data.get("telegram_username"), data["name"],
                 data["service"], data["phone"], data["comment"], created_at),
            )
            await db.commit()
            return int(cursor.lastrowid), created_at

    async def get_latest(self, limit: int = 10) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA busy_timeout=5000")
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM leads ORDER BY created_at DESC, id DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in await cursor.fetchall()]

    async def get_stats(self) -> tuple[int, list[tuple[str, int]]]:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA busy_timeout=5000")
            total_cursor = await db.execute("SELECT COUNT(*) FROM leads")
            total = int((await total_cursor.fetchone())[0])
            cursor = await db.execute(
                "SELECT service, COUNT(*) FROM leads GROUP BY service ORDER BY service"
            )
            return total, [(str(row[0]), int(row[1])) for row in await cursor.fetchall()]
