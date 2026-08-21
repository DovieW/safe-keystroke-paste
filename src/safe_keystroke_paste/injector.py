"""Paced keystroke injection through ydotool."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import dataclass

from .control import InstanceControl


class InjectionError(RuntimeError):
    """Raised when the injection backend is unavailable or fails."""


@dataclass(frozen=True)
class InjectionOptions:
    key_delay_ms: int = 15
    focus_delay_ms: int = 500


def inject(
    text: str,
    control: InstanceControl,
    options: InjectionOptions | None = None,
) -> bool:
    options = options or InjectionOptions()
    executable = shutil.which("ydotool")
    if executable is None:
        raise InjectionError("ydotool is required.")
    socket_path = os.environ.get("YDOTOOL_SOCKET")
    if socket_path and not os.path.exists(socket_path):
        raise InjectionError(f"The ydotool socket does not exist: {socket_path}")

    deadline = time.monotonic() + options.focus_delay_ms / 1000
    while time.monotonic() < deadline:
        if control.cancellation_requested():
            return False
        time.sleep(0.025)

    process = subprocess.Popen(
        [executable, "type", "--key-delay", str(options.key_delay_ms), "--file", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    process.stdin.write(text.encode("utf-8"))
    process.stdin.close()
    while process.poll() is None:
        if control.cancellation_requested():
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            _release_modifiers(executable)
            return False
        time.sleep(0.025)
    if process.returncode != 0:
        assert process.stderr is not None
        detail = process.stderr.read().decode("utf-8", "replace").strip()
        raise InjectionError(detail or f"ydotool exited with {process.returncode}.")
    return True


def _release_modifiers(executable: str) -> None:
    # Linux input keycodes: left/right Ctrl, Shift, Alt, and Meta.
    releases = ["29:0", "97:0", "42:0", "54:0", "56:0", "100:0", "125:0", "126:0"]
    subprocess.run(
        [executable, "key", *releases],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=2,
    )
