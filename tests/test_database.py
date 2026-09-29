import asyncio

from app.database import Database


def test_database_creates_leads_and_persists_language(tmp_path) -> None:
    async def scenario() -> None:
        database = Database(str(tmp_path / "leads.db"))
        await database.initialize()

        assert await database.get_language(100) == "en"
        await database.set_language(100, "ru")
        assert await database.get_language(100) == "ru"

        lead_id, created_at = await database.create_lead(
            {
                "telegram_user_id": 100,
                "telegram_username": "demo_user",
                "name": "Alex",
                "service": "telegram_bot",
                "phone": "+77001234567",
                "comment": "Need a Telegram bot.",
            }
        )

        leads = await database.get_latest()
        total, stats = await database.get_stats()

        assert lead_id == 1
        assert created_at.endswith("+00:00")
        assert leads[0]["service"] == "telegram_bot"
        assert total == 1
        assert stats == [("telegram_bot", 1)]

    asyncio.run(scenario())
