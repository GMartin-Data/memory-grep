"""Phase 3 unit tests for scanner discovery, incl. PRD R5 exclusion.

R5: the glob `*/memory/*.md` must match per-project memory files but must NOT
pick up agent memory (`agent-memory/<agent>/MEMORY.md`), which is out of scope
for v1 (PRD success criterion #7).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from memgrep.scanner import discover_memory_files


def test_discovers_per_project_memory_files(tmp_path: Path) -> None:
    memory = tmp_path / "proj-a" / "memory"
    memory.mkdir(parents=True)
    note = memory / "note.md"
    note.write_text("body\n", encoding="utf-8")

    assert discover_memory_files(tmp_path) == [note]


def test_excludes_agent_memory(tmp_path: Path) -> None:
    # Legitimate per-project memory file (must be found).
    project_memory = tmp_path / "proj-a" / "memory"
    project_memory.mkdir(parents=True)
    kept = project_memory / "kept.md"
    kept.write_text("findme\n", encoding="utf-8")

    # Agent memory nested under agent-memory/<agent>/ (must be excluded).
    agent_memory = tmp_path / "agent-memory" / "some-agent"
    agent_memory.mkdir(parents=True)
    (agent_memory / "MEMORY.md").write_text("findme\n", encoding="utf-8")

    # A memory/ dir nested deeper than one segment is also out of glob reach.
    nested = tmp_path / "proj-a" / "sub" / "memory"
    nested.mkdir(parents=True)
    (nested / "deep.md").write_text("findme\n", encoding="utf-8")

    found = discover_memory_files(tmp_path)

    assert found == [kept]


def test_missing_dir_raises_file_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        discover_memory_files(missing)
