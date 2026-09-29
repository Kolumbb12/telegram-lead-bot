DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = frozenset({"en", "ru"})

TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "welcome": "Welcome! I can help you submit a request for development or automation.",
        "help": "To submit a request, tap «📝 Submit a lead» and complete the form. Use /cancel to stop at any time.",
        "cancelled": "Lead submission cancelled.",
        "choose_service": "Choose a service:",
        "ask_name": "What is your name?",
        "invalid_name": "Please enter a name between 2 and 100 characters.",
        "ask_phone": "Enter your phone number or use the button below:",
        "foreign_contact": "Please share your own contact or enter the number manually.",
        "invalid_phone": "I could not recognize the number. Enter a phone number with 10 to 15 digits.",
        "ask_comment": "Briefly describe your task:",
        "invalid_comment": "The description must contain 3 to 2,000 characters.",
        "lead_summary": "<b>New lead</b>\n\nName: {name}\nService: {service}\nPhone: {phone}\nDescription: {comment}",
        "lead_sent": "✅ Your request has been sent.\nThank you! You will be contacted after it is reviewed.",
        "lead_cancelled": "Lead cancelled.",
        "lead_submit_failed": "The request could not be sent. Please try again.",
        "language_prompt": "Choose your language:",
        "language_saved": "Language set to English.",
        "about": "This bot collects client leads and sends them to an administrator. Use /help for assistance.",
        "admin_lead": "📩 <b>New lead #{lead_id}</b>\n\nName: {name}\nTelegram: {username} (ID: {user_id})\nService: {service}\nPhone: {phone}\nDescription: {comment}\nCreated: {created_at}",
        "latest_leads": "<b>Latest leads:</b>",
        "no_leads": "There are no leads yet.",
        "phone_label": "Phone",
        "statistics": "<b>Lead statistics</b>\n\nTotal: {total}\n\n{details}",
        "no_service_data": "No service data",
        "unknown_username": "not set",
        "stale_option": "This option is no longer available.",
    },
    "ru": {
        "welcome": "Здравствуйте! Я помогу оставить заявку на разработку или автоматизацию.",
        "help": "Чтобы оставить заявку, нажмите «📝 Оставить заявку» и заполните форму. Для отмены в любой момент используйте /cancel.",
        "cancelled": "Заполнение заявки отменено.",
        "choose_service": "Выберите услугу:",
        "ask_name": "Как вас зовут?",
        "invalid_name": "Введите имя длиной от 2 до 100 символов.",
        "ask_phone": "Укажите номер телефона или воспользуйтесь кнопкой ниже:",
        "foreign_contact": "Отправьте свой контакт или введите номер вручную.",
        "invalid_phone": "Не удалось распознать номер. Введите номер длиной от 10 до 15 цифр.",
        "ask_comment": "Кратко опишите вашу задачу:",
        "invalid_comment": "Описание должно содержать от 3 до 2 000 символов.",
        "lead_summary": "<b>Новая заявка</b>\n\nИмя: {name}\nУслуга: {service}\nТелефон: {phone}\nКомментарий: {comment}",
        "lead_sent": "✅ Заявка отправлена.\nСпасибо! С вами свяжутся после рассмотрения заявки.",
        "lead_cancelled": "Заявка отменена.",
        "lead_submit_failed": "Не удалось отправить заявку. Попробуйте ещё раз.",
        "language_prompt": "Выберите язык:",
        "language_saved": "Выбран русский язык.",
        "about": "Этот бот собирает заявки клиентов и передаёт их администратору. /help — справка.",
        "admin_lead": "📩 <b>Новая заявка #{lead_id}</b>\n\nИмя: {name}\nTelegram: {username} (ID: {user_id})\nУслуга: {service}\nТелефон: {phone}\nКомментарий: {comment}\nДата создания: {created_at}",
        "latest_leads": "<b>Последние заявки:</b>",
        "no_leads": "Заявок пока нет.",
        "phone_label": "Телефон",
        "statistics": "<b>Статистика заявок</b>\n\nВсего: {total}\n\n{details}",
        "no_service_data": "Нет данных по услугам",
        "unknown_username": "не указан",
        "stale_option": "Этот вариант больше недоступен.",
    },
}

BUTTONS: dict[str, dict[str, str]] = {
    "en": {
        "lead": "📝 Submit a lead", "language": "🌐 Language", "about": "ℹ️ About",
        "share_phone": "📱 Share phone number", "submit": "✅ Submit",
        "restart": "✏️ Start over", "cancel": "❌ Cancel",
    },
    "ru": {
        "lead": "📝 Оставить заявку", "language": "🌐 Язык", "about": "ℹ️ О боте",
        "share_phone": "📱 Отправить номер телефона", "submit": "✅ Отправить",
        "restart": "✏️ Заполнить заново", "cancel": "❌ Отмена",
    },
}

SERVICES: dict[str, dict[str, str]] = {
    "en": {"telegram_bot": "Telegram bot", "automation": "Automation", "data_parsing": "Data parsing", "other": "Other"},
    "ru": {"telegram_bot": "Telegram-бот", "automation": "Автоматизация", "data_parsing": "Парсинг данных", "other": "Другое"},
}

# Existing databases may contain labels from earlier versions of the bot.
LEGACY_SERVICE_CODES = {
    "Telegram-бот": "telegram_bot", "Telegram bot": "telegram_bot",
    "Автоматизация": "automation", "Automation": "automation",
    "Парсинг данных": "data_parsing", "Data parsing": "data_parsing",
    "Другое": "other", "Other": "other",
}


def normalize_language(language: str | None) -> str:
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def text(language: str | None, key: str, **values: object) -> str:
    return TEXTS[normalize_language(language)][key].format(**values)


def button(language: str | None, key: str) -> str:
    return BUTTONS[normalize_language(language)][key]


def service_name(service: str, language: str | None) -> str:
    code = LEGACY_SERVICE_CODES.get(service, service)
    return SERVICES[normalize_language(language)].get(code, service)


def all_button_values(key: str) -> frozenset[str]:
    return frozenset(labels[key] for labels in BUTTONS.values())
