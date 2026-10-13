"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .clipboard import ClipboardError, read_text
from .control import AlreadyRunning, InstanceControl, request_cancel
from .injector import InjectionError, InjectionOptions, inject
from .validation import UnsafeText, validate_text


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="skpaste",
        description="Preview and safely type clipboard text as paced keystrokes.",
    )
    result.add_argument("--version", action="version", version=__version__)
    subcommands = result.add_subparsers(dest="command")
    send = subcommands.add_parser("send", help="preview and type clipboard text")
    send.add_argument("--key-delay", type=int, default=15, metavar="MS")
    send.add_argument("--focus-delay", type=int, default=500, metavar="MS")
    send.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and preview without injecting input",
    )
    subcommands.add_parser("cancel", help="cancel an active transmission")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if arguments.command == "cancel":
        if request_cancel():
            print("Cancellation requested.")
            return 0
        print("No active transmission.", file=sys.stderr)
        return 1
    if arguments.command not in (None, "send"):
        return 2
    if arguments.command is None:
        arguments = parser().parse_args(["send"])
    if not 1 <= arguments.key_delay <= 1000:
        return _error("--key-delay must be between 1 and 1000 milliseconds.")
    if not 100 <= arguments.focus_delay <= 10000:
        return _error("--focus-delay must be between 100 and 10000 milliseconds.")

    try:
        text = read_text()
        control = InstanceControl.acquire()
    except (ClipboardError, UnsafeText, AlreadyRunning) as exc:
        return _error(str(exc))

    try:
        from PyQt6.QtWidgets import QApplication, QDialog

        from .ui import PreviewDialog

        application = QApplication.instance() or QApplication(sys.argv[:1])
        dialog = PreviewDialog(text, arguments.focus_delay)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return 0
        text = validate_text(dialog.text())
        dialog.hide()
        application.processEvents()
        if arguments.dry_run:
            print(f"Dry run approved {len(text)} characters; no keys were sent.")
            return 0
        completed = inject(
            text,
            control,
            InjectionOptions(
                key_delay_ms=arguments.key_delay,
                focus_delay_ms=arguments.focus_delay,
            ),
        )
        return 0 if completed else 130
    except (ImportError, InjectionError, UnsafeText) as exc:
        return _error(str(exc))
    finally:
        control.close()


def _error(message: str) -> int:
    print(f"skpaste: {message}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
