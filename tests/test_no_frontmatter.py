"""Phase 3 integration test: PRD case 7 — file without frontmatter.

A memory file that has no `---` block is not an error: its content is scanned
and the per-file header is rendered with the path only, without the
`[name: ... | type: ...]` line.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run_memgrep(args: list[str], fake_home: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "HOME": str(fake_home)}
    return subprocess.run(
        [sys.executable, "-m", "memgrep", *args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_file_without_frontmatter_header_has_path_only(tmp_path: Path) -> None:
    memory = tmp_path / ".claude" / "projects" / "proj-x" / "memory"
    memory.mkdir(parents=True)
    plain = memory / "plain.md"
    plain.write_text("Just a raw note, findme here.\n", encoding="utf-8")

    result = _run_memgrep(["findme"], tmp_path)

    assert result.returncode == 0, result.stderr
    assert "findme" in result.stdout
    # The header is the file path; no metadata brackets are emitted.
    assert str(plain) in result.stdout
    assert "[name:" not in result.stdout
    assert "| type:" not in result.stdout
