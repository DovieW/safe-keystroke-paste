from pathlib import Path

from safe_keystroke_paste.control import InstanceControl
from safe_keystroke_paste.injector import InjectionOptions, inject


def test_injector_passes_snapshot_over_stdin(monkeypatch, tmp_path: Path):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(runtime))
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    output = tmp_path / "typed"
    ydotool = fake_bin / "ydotool"
    ydotool.write_text(
        "#!/bin/sh\n"
        "shift\n"
        'while [ "$#" -gt 0 ]; do\n'
        '  if [ "$1" = --file ]; then shift 2; '
        'cat >"$SKPASTE_TEST_OUTPUT"; exit; fi\n'
        "  shift\n"
        "done\n"
    )
    ydotool.chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake_bin}:{Path('/usr/bin')}")
    monkeypatch.setenv("SKPASTE_TEST_OUTPUT", str(output))

    control = InstanceControl.acquire()
    try:
        assert inject(
            "safe text",
            control,
            InjectionOptions(key_delay_ms=1, focus_delay_ms=1),
        )
    finally:
        control.close()
    assert output.read_text() == "safe text"
