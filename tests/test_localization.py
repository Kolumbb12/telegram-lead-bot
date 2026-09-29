from app.keyboards import confirmation_menu, main_menu, service_menu
from app.localization import DEFAULT_LANGUAGE, service_name, text


def test_english_is_the_default_language() -> None:
    assert DEFAULT_LANGUAGE == "en"
    assert text(None, "welcome").startswith("Welcome")


def test_service_labels_support_current_and_legacy_values() -> None:
    assert service_name("telegram_bot", "ru") == "Telegram-бот"
    assert service_name("Telegram-бот", "en") == "Telegram bot"


def test_keyboards_are_localized() -> None:
    assert main_menu("en").keyboard[0][0].text == "📝 Submit a lead"
    assert main_menu("ru").keyboard[0][0].text == "📝 Оставить заявку"
    assert service_menu("en").inline_keyboard[0][0].text == "Telegram bot"
    assert confirmation_menu("ru").inline_keyboard[0][0].text == "✅ Отправить"
