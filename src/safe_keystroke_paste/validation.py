"""Safety validation for clipboard snapshots."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyPolicy:
    max_characters: int = 256


class UnsafeText(ValueError):
    """Raised when clipboard text violates the configured safety policy."""


def validate_text(text: str, policy: SafetyPolicy | None = None) -> str:
    policy = policy or SafetyPolicy()
    if not text:
        raise UnsafeText("The clipboard does not contain any text.")
    if len(text) > policy.max_characters:
        raise UnsafeText(
            f"Clipboard text contains {len(text)} characters; "
            f"the limit is {policy.max_characters}."
        )

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
