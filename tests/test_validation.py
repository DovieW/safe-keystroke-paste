import pytest

from safe_keystroke_paste.validation import SafetyPolicy, UnsafeText, validate_text


def test_accepts_short_single_line_text():
    assert validate_text("Hello, remote world!") == "Hello, remote world!"


@pytest.mark.parametrize("text", ["one\ntwo", "one\rtwo", "one\ttwo", "a\x1bb"])
def test_rejects_actionable_control_characters(text):
    with pytest.raises(UnsafeText):
        validate_text(text)


def test_rejects_empty_and_oversized_text():
    with pytest.raises(UnsafeText):
        validate_text("")
    with pytest.raises(UnsafeText):
        validate_text("abcd", SafetyPolicy(max_characters=3))
