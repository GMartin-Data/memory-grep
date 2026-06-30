"""Typer CLI for memgrep."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from memgrep.formatter import SUMMARY_SEPARATOR, format_file_block, format_summary
from memgrep.frontmatter import InvalidFrontmatterError, parse_frontmatter
from memgrep.matcher import find_matches
from memgrep.scanner import discover_memory_files

DEFAULT_PROJECTS_DIR = Path.home() / ".claude" / "projects"
VALID_TYPES = ("user", "feedback", "project", "reference")

app = typer.Typer(
    add_completion=False,
    help="Grep across Claude Code persistent memory.",
)


@app.command()
def main(
    pattern: str = typer.Argument(..., help="Substring to search for (smart-case)."),
    type_filter: str | None = typer.Option(
        None,
        "--type",
        help="Restrict to memory of this type: user, feedback, project, reference.",
    ),
) -> None:
    if type_filter is not None and type_filter not in VALID_TYPES:
        typer.echo(
            f"Invalid --type '{type_filter}'. Valid values: {', '.join(VALID_TYPES)}.",
            err=True,
        )
        raise typer.Exit(code=2)

    projects_dir = DEFAULT_PROJECTS_DIR

    try:
        memory_files = discover_memory_files(projects_dir)
    except FileNotFoundError:
        typer.echo(f"No memory directory found at {projects_dir}", err=True)
        raise typer.Exit(code=2) from None

    color = sys.stdout.isatty()
    total_matches = 0
    matched_files = 0

    for file_path in memory_files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            typer.echo(f"{file_path}: cannot read ({exc})", err=True)
            continue

        try:
            metadata = parse_frontmatter(content)[0]
        except InvalidFrontmatterError:
            typer.echo(
                f"{file_path}: invalid frontmatter, scanning content only", err=True
            )
            metadata = None

        if type_filter is not None:
            file_type = metadata.get("type") if metadata else None
            if file_type != type_filter:
                continue

        matches = find_matches(content, pattern)
        if matches:
            total_matches += len(matches)
            matched_files += 1
            block = format_file_block(
                file_path,
                metadata,
                content.splitlines(),
                matches,
                color=color,
                pattern=pattern,
            )
            typer.echo(block)
            typer.echo()

    if total_matches == 0:
        sys.exit(1)

    typer.echo(SUMMARY_SEPARATOR)
    typer.echo(format_summary(total_matches, matched_files))
