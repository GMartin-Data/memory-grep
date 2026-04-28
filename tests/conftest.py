"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fake_home(tmp_path: Path) -> Path:
    """Build a fake `$HOME` containing `.claude/projects/<proj>/memory/*.md`.

    Layout created:
        <tmp_path>/.claude/projects/proj-a/memory/feedback_one.md
        <tmp_path>/.claude/projects/proj-a/memory/user_role.md
        <tmp_path>/.claude/projects/proj-b/memory/project_init.md

    Returns the fake home path. Use it as `HOME=<fake_home>` when invoking
    `memgrep` via subprocess.
    """
    projects = tmp_path / ".claude" / "projects"

    proj_a_memory = projects / "proj-a" / "memory"
    proj_a_memory.mkdir(parents=True)
    (proj_a_memory / "feedback_one.md").write_text(
        "---\nname: feedback one\ntype: feedback\n---\nUser hates noisy output.\n",
        encoding="utf-8",
    )
    (proj_a_memory / "user_role.md").write_text(
        "---\nname: user role\ntype: user\n---\nData engineer with Python focus.\n",
        encoding="utf-8",
    )

    proj_b_memory = projects / "proj-b" / "memory"
    proj_b_memory.mkdir(parents=True)
    (proj_b_memory / "project_init.md").write_text(
        "---\nname: project init\ntype: project\n---\nBootstrap phase, dogfooding ongoing.\n",
        encoding="utf-8",
    )

    return tmp_path
