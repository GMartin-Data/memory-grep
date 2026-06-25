"""Phase 1b integration tests: --type filter and frontmatter matching."""

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


def test_type_filter_restricts_to_matching_type(fake_home: Path) -> None:
    # "engineer" appears in user_role.md (type: user) only.
    result = _run_memgrep(["--type", "user", "engineer"], fake_home)

    assert result.returncode == 0, result.stderr
    assert "user_role.md" in result.stdout
    assert "feedback_one.md" not in result.stdout
    assert "project_init.md" not in result.stdout


def test_type_filter_excludes_other_types(fake_home: Path) -> None:
    # "dogfooding" exists in project_init.md (type: project); filtering on
    # feedback must yield nothing -> exit 1.
    result = _run_memgrep(["--type", "feedback", "dogfooding"], fake_home)

    assert result.returncode == 1
    assert result.stdout == ""


def test_invalid_type_exits_with_code_2(fake_home: Path) -> None:
    result = _run_memgrep(["--type", "bogus", "anything"], fake_home)

    assert result.returncode == 2
    # Message must list the four valid types.
    for valid in ("user", "feedback", "project", "reference"):
        assert valid in result.stderr


def test_match_in_frontmatter_name(fake_home: Path) -> None:
    # "feedback one" is the name in feedback_one.md frontmatter.
    result = _run_memgrep(["one"], fake_home)

    assert result.returncode == 0, result.stderr
    assert "feedback_one.md" in result.stdout


def test_malformed_frontmatter_warns_and_scans_content(tmp_path: Path) -> None:
    memory = tmp_path / ".claude" / "projects" / "proj-x" / "memory"
    memory.mkdir(parents=True)
    (memory / "broken.md").write_text(
        "---\nname: : broken: :\n  bad indent\n---\nfindme in body.\n",
        encoding="utf-8",
    )

    result = _run_memgrep(["findme"], tmp_path)

    assert result.returncode == 0, result.stderr
    assert "findme" in result.stdout
    assert "invalid frontmatter" in result.stderr
