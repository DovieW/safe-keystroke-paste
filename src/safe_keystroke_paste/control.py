"""Single-flight ownership and cancellation over a private Unix socket."""

from __future__ import annotations

import fcntl
import os
import socket
from dataclasses import dataclass
from pathlib import Path


class AlreadyRunning(RuntimeError):
    """Raised when another transmission owns the single-flight lock."""


def runtime_directory() -> Path:
    base = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
    directory = base / "safe-keystroke-paste"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory.chmod(0o700)
    return directory


@dataclass
class InstanceControl:
    lock_handle: object
    listener: socket.socket
    socket_path: Path

    @classmethod
    def acquire(cls) -> InstanceControl:
        directory = runtime_directory()
        lock_path = directory / "transmission.lock"
        lock_handle = lock_path.open("a+")
        try:
            fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            lock_handle.close()
            raise AlreadyRunning("Another safe paste is already active.") from exc

        socket_path = directory / "control.sock"
        socket_path.unlink(missing_ok=True)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(str(socket_path))
        socket_path.chmod(0o600)
        listener.listen(1)
        listener.setblocking(False)
        return cls(lock_handle, listener, socket_path)

    def cancellation_requested(self) -> bool:
        try:
            connection, _ = self.listener.accept()
        except BlockingIOError:
            return False
        with connection:
            return connection.recv(32) == b"CANCEL\n"

    def close(self) -> None:
        self.listener.close()
        self.socket_path.unlink(missing_ok=True)
        fcntl.flock(self.lock_handle, fcntl.LOCK_UN)
        self.lock_handle.close()


def request_cancel() -> bool:
    socket_path = runtime_directory() / "control.sock"
    if not socket_path.exists():
        return False
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(1.0)
    try:
        client.connect(str(socket_path))
        client.sendall(b"CANCEL\n")
    except (ConnectionError, OSError):
        return False
    finally:
        client.close()
    return True
