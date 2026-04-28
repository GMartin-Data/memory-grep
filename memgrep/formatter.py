"""Output formatting (Phase 1a: plain `<path>:<lineno>:<line>`)."""

from __future__ import annotations

from pathlib import Path

from memgrep.matcher import Match


def format_match(file_path: Path, match: Match) -> str:
    return f"{file_path}:{match.lineno}:{match.line}"
