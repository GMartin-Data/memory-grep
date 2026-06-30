"""Phase 2 integration test: PRD case 5 — unreadable file is skipped gracefully."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


def _run_memgrep(args: list[str], fake_home: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HOME": str(fake_home)}
    return subprocess.run(
        [sys.executable, "-m", "memgrep", *args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_unreadable_file_is_skipped_others_still_scanned(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root bypasses file permissions; chmod 000 has no effect")

    memory = tmp_path / ".claude" / "projects" / "proj-x" / "memory"
    memory.mkdir(parents=True)

    unreadable = memory / "locked.md"
    unreadable.write_text("findme in locked file.\n", encoding="utf-8")
    unreadable.chmod(0o000)

    readable = memory / "open.md"
    readable.write_text("findme in open file.\n", encoding="utf-8")

    try:
        result = _run_memgrep(["findme"], tmp_path)
    finally:
        # Restore perms so pytest's tmp_path cleanup can remove the file.
        unreadable.chmod(0o644)

    # The readable file still matches -> exit 0, not a crash.
    assert result.returncode == 0, result.stderr
    assert "open.md" in result.stdout
    assert "findme in open file." in result.stdout

    # The unreadable file is reported on stderr and excluded from stdout.
    assert "locked.md" in result.stderr
    assert "cannot read" in result.stderr
    assert "locked.md" not in result.stdout
