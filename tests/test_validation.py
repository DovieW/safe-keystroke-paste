import pytest

from safe_keystroke_paste.validation import UnsafeText, validate_text


def test_accepts_short_single_line_text():
    assert validate_text("Hello, remote world!") == "Hello, remote world!"


@pytest.mark.parametrize("text", ["one\ntwo", "one\rtwo", "one\ttwo", "a\x1bb"])
def test_rejects_actionable_control_characters(text):
    with pytest.raises(UnsafeText):
        validate_text(text)


def test_rejects_empty_text_but_accepts_text_of_any_length():
    with pytest.raises(UnsafeText):
        validate_text("")
    long_text = "a" * 100_000
    assert validate_text(long_text) == long_text
