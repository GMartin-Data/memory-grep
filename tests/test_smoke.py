"""Phase 1a smoke test: `memgrep <pattern>` end-to-end via subprocess."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run_memgrep(pattern: str, fake_home: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HOME": str(fake_home)}
    return subprocess.run(
        [sys.executable, "-m", "memgrep", pattern],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_smoke_finds_match_in_fake_home(fake_home: Path) -> None:
    result = _run_memgrep("dogfooding", fake_home)

    assert result.returncode == 0, f"expected 0, got {result.returncode}\nstderr={result.stderr}"
    assert "project_init.md" in result.stdout
    assert "dogfooding" in result.stdout


def test_no_matches_exits_with_code_1(fake_home: Path) -> None:
    result = _run_memgrep("zzz_no_such_pattern_zzz", fake_home)

    assert result.returncode == 1
    assert result.stdout == ""


def test_missing_projects_dir_exits_with_code_2(tmp_path: Path) -> None:
    # Empty fake home, no .claude/projects/ inside.
    result = _run_memgrep("anything", tmp_path)

    assert result.returncode == 2
    assert "No memory directory found" in result.stderr


def test_empty_projects_dir_exits_with_code_1(tmp_path: Path) -> None:
    # .claude/projects/ exists but contains no memory files.
    (tmp_path / ".claude" / "projects").mkdir(parents=True)
    result = _run_memgrep("anything", tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
