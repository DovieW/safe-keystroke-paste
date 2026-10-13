"""Editable confirmation UI that leaves the system clipboard untouched."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from .validation import UnsafeText, validate_text


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
        self.preview = preview
        preview.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        preview.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        preview.setAccessibleName("Clipboard text preview")
        layout.addWidget(preview)

        replace = QPushButton("Replace line breaks with spaces")
        replace.clicked.connect(self.replace_line_breaks)
        layout.addWidget(replace)
        self.validation_error = QLabel()
        self.validation_error.setWordWrap(True)
        layout.addWidget(self.validation_error)

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
        self.send_button = send
        send.setText("Type as keystrokes")
        send.setDefault(False)
        send.setAutoDefault(False)
        buttons.accepted.connect(self.accept_validated)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        preview.textChanged.connect(self.update_validation)
        self.update_validation()

    def text(self) -> str:
        return self.preview.toPlainText()

    def replace_line_breaks(self) -> None:
        self.preview.setPlainText(
            self.text().replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
        )

    def update_validation(self) -> bool:
        try:
            validate_text(self.text())
        except UnsafeText as exc:
            message = str(exc)
            if "line breaks" in message:
                message += (
                    " Line breaks can send Enter and submit commands or forms."
                    " Replace them with spaces or edit the text."
                )
            self.validation_error.setText(message)
            self.send_button.setEnabled(False)
            return False
        self.validation_error.setText(
            f"Ready to type {len(self.text())} characters. "
            "Edits do not change your clipboard."
        )
        self.send_button.setEnabled(True)
        return True

    def accept_validated(self) -> None:
        if self.update_validation():
            self.accept()
