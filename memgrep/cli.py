"""Typer CLI for memgrep."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from memgrep.formatter import format_match
from memgrep.matcher import find_matches
from memgrep.scanner import discover_memory_files

DEFAULT_PROJECTS_DIR = Path.home() / ".claude" / "projects"

app = typer.Typer(
    add_completion=False,
    help="Grep across Claude Code persistent memory.",
)


@app.command()
def main(
    pattern: str = typer.Argument(..., help="Substring to search for (smart-case)."),
) -> None:
    projects_dir = DEFAULT_PROJECTS_DIR

    try:
        memory_files = discover_memory_files(projects_dir)
    except FileNotFoundError:
        typer.echo(f"No memory directory found at {projects_dir}", err=True)
        raise typer.Exit(code=2) from None

    total_matches = 0
    files_with_matches = 0

    for file_path in memory_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            typer.echo(f"{file_path}: cannot read ({exc})", err=True)
            continue

        matches = find_matches(content, pattern)
        if matches:
            files_with_matches += 1
            total_matches += len(matches)
            for match in matches:
                typer.echo(format_match(file_path, match))

    if total_matches == 0:
        sys.exit(1)
