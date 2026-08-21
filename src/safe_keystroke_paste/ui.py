"""Minimal confirmation UI that never mutates the clipboard snapshot."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
)


class PreviewDialog(QDialog):
    def __init__(self, text: str, focus_delay_ms: int) -> None:
        super().__init__()
        self.setWindowTitle("Safe Keystroke Paste")
        self.setMinimumSize(680, 360)

        layout = QVBoxLayout(self)
        heading = QLabel(
            f"Review {len(text)} characters. After approval, refocus the target "
            f"within {focus_delay_ms / 1000:.1f} seconds."
        )
        heading.setWordWrap(True)
        layout.addWidget(heading)

        preview = QPlainTextEdit(text)
        preview.setReadOnly(True)
        preview.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        preview.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        preview.setAccessibleName("Clipboard text preview")
        layout.addWidget(preview)

        warning = QLabel(
            "Keystrokes go to whichever window has focus. Cancel immediately if "
            "focus changes unexpectedly."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #b45309; font-weight: 600;")
        layout.addWidget(warning)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        send = buttons.button(QDialogButtonBox.StandardButton.Ok)
        send.setText("Type as keystrokes")
        send.setDefault(False)
        send.setAutoDefault(False)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
