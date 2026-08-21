"""Safety validation for clipboard snapshots."""

from __future__ import annotations

import unicodedata


class UnsafeText(ValueError):
    """Raised when clipboard text violates the configured safety policy."""


def validate_text(text: str) -> str:
    if not text:
        raise UnsafeText("The clipboard does not contain any text.")
    prohibited = []
    for character in text:
        if character in "\r\n":
            prohibited.append("line breaks")
        elif character == "\t":
            prohibited.append("tabs")
        elif unicodedata.category(character) == "Cc":
            prohibited.append("control characters")
    if prohibited:
        kinds = ", ".join(dict.fromkeys(prohibited))
        raise UnsafeText(f"Clipboard text contains prohibited {kinds}.")
    return text
