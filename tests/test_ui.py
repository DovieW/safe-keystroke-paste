import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import (  # noqa: E402
    QApplication,
    QDialogButtonBox,
    QPlainTextEdit,
)

from safe_keystroke_paste.ui import PreviewDialog  # noqa: E402


def test_preview_is_editable_and_send_is_not_default():
    application = QApplication.instance() or QApplication([])
    dialog = PreviewDialog("artificial canary", 500)
    preview = dialog.findChild(QPlainTextEdit)
    buttons = dialog.findChild(QDialogButtonBox)
    assert preview is not None and not preview.isReadOnly()
    assert buttons is not None
    send = buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert not send.isDefault()
    assert not send.autoDefault()
    dialog.close()
    application.processEvents()


def test_editing_and_replacing_line_breaks_revalidates():
    application = QApplication.instance() or QApplication([])
    dialog = PreviewDialog("first\r\nsecond\nthird", 500)
    assert not dialog.send_button.isEnabled()
    assert "line breaks" in dialog.validation_error.text()
    dialog.accept_validated()
    assert dialog.result() == 0
    dialog.replace_line_breaks()
    assert dialog.text() == "first second third"
    assert dialog.send_button.isEnabled()
    for invalid in ("", "tab\there", "control\x01"):
        dialog.preview.setPlainText(invalid)
        assert not dialog.send_button.isEnabled()
    dialog.preview.setPlainText("edited text")
    assert dialog.send_button.isEnabled()
    dialog.accept_validated()
    assert dialog.result() == 1
    dialog.close()
    application.processEvents()
