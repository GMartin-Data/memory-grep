"""Filesystem discovery: locate memory files to scan."""

from __future__ import annotations

from pathlib import Path

MEMORY_GLOB = "*/memory/*.md"


def discover_memory_files(projects_dir: Path) -> list[Path]:
    """Return sorted list of memory `.md` files under `projects_dir`.

    Uses the glob `*/memory/*.md` to match exactly the per-project memory layout
    (`~/.claude/projects/<project>/memory/<file>.md`). The single-segment
    wildcard `*/memory/*.md` does NOT recurse into nested `agent-memory/`
    directories — R5 of the PRD (exclusion of `claude/agent-memory/<agent>/MEMORY.md`)
    is satisfied by construction.
    """
    if not projects_dir.is_dir():
        raise FileNotFoundError(projects_dir)
    return sorted(projects_dir.glob(MEMORY_GLOB))
