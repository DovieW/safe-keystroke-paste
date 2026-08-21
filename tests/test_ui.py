import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import (  # noqa: E402
    QApplication,
    QDialogButtonBox,
    QPlainTextEdit,
)

from safe_keystroke_paste.ui import PreviewDialog  # noqa: E402


def test_preview_is_read_only_and_send_is_not_default():
    application = QApplication.instance() or QApplication([])
    dialog = PreviewDialog("artificial canary", 500)
    preview = dialog.findChild(QPlainTextEdit)
    buttons = dialog.findChild(QDialogButtonBox)
    assert preview is not None and preview.isReadOnly()
    assert buttons is not None
    send = buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert not send.isDefault()
    assert not send.autoDefault()
    dialog.close()
    application.processEvents()
