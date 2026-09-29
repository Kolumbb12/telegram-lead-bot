from app.handlers import escaped_preview, normalize_phone, valid_phone


def test_phone_validation_and_normalization() -> None:
    assert valid_phone("+7 (700) 123-45-67")
    assert not valid_phone("call 77001234567")
    assert normalize_phone("+7 (700) 123-45-67") == "+77001234567"


def test_escaped_preview_preserves_valid_html_entities() -> None:
    preview = escaped_preview("&" * 1000, 100)

    assert preview == "&amp;" * 20 + "…"
