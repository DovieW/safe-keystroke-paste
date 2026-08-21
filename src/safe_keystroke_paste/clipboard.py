"""Clipboard acquisition with no history-manager dependency."""

from __future__ import annotations

import os
import shutil
import subprocess


class ClipboardError(RuntimeError):
    """Raised when a clipboard snapshot cannot be acquired safely."""


def read_text(*, timeout: float = 5.0) -> str:
    if not os.environ.get("WAYLAND_DISPLAY"):
        raise ClipboardError("A Wayland session is required.")
    executable = shutil.which("wl-paste")
    if executable is None:
        raise ClipboardError("wl-paste is required; install wl-clipboard.")
    try:
        result = subprocess.run(
            [executable, "--no-newline", "--type", "text"],
            check=False,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise ClipboardError("The clipboard request timed out.") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise ClipboardError(detail or "The clipboard does not contain text.")
    try:
        return result.stdout.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise ClipboardError("Clipboard text is not valid UTF-8.") from exc
