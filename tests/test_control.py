import socket
from pathlib import Path

import pytest

from safe_keystroke_paste.control import AlreadyRunning, InstanceControl


def test_single_flight_lock_and_cancel(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path))
    first = InstanceControl.acquire()
    try:
        with pytest.raises(AlreadyRunning):
            InstanceControl.acquire()
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(first.socket_path))
        client.sendall(b"CANCEL\n")
        client.close()
        assert first.cancellation_requested()
    finally:
        first.close()
