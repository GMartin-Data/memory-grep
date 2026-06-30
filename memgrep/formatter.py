"""Output formatting (Phase 2: enriched per-file blocks with context)."""

from __future__ import annotations

from pathlib import Path

from memgrep.matcher import Match, is_smart_case_insensitive

ANSI_HIGHLIGHT = "\x1b[1;31m"  # bold red
ANSI_RESET = "\x1b[0m"

HEADER_FIELDS = ("name", "type")


def _format_header(file_path: Path, metadata: dict | None) -> str:
    """Render the file header: `<path>` plus `[name: X | type: Y]` for present fields."""
    if not metadata:
        return str(file_path)

    parts = [f"{field}: {metadata[field]}" for field in HEADER_FIELDS if field in metadata]
    if not parts:
        return str(file_path)
    return f"{file_path}  [{' | '.join(parts)}]"


def _merge_windows(linenos: list[int], context: int, last_line: int) -> list[tuple[int, int]]:
    """Merge per-match context windows into sorted, non-overlapping (start, end) ranges.

    Windows are `[lineno - context, lineno + context]`, clamped to `[1, last_line]`.
    Adjacent or overlapping windows are merged (grep -C behaviour: no duplicated
    lines, no separator between them).
    """
    windows = sorted((max(1, n - context), min(last_line, n + context)) for n in linenos)
    merged: list[tuple[int, int]] = []
    for start, end in windows:
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _highlight(line: str, pattern: str) -> str:
    """Wrap each occurrence of `pattern` in `line` with ANSI highlight codes.

    Honours smart-case: case-insensitive search when `pattern` is all-lowercase.
    """
    if not pattern:
        return line

    insensitive = is_smart_case_insensitive(pattern)
    haystack = line.lower() if insensitive else line
    needle = pattern.lower() if insensitive else pattern

    result = []
    cursor = 0
    while True:
        index = haystack.find(needle, cursor)
        if index == -1:
            result.append(line[cursor:])
            break
        result.append(line[cursor:index])
        result.append(f"{ANSI_HIGHLIGHT}{line[index : index + len(needle)]}{ANSI_RESET}")
        cursor = index + len(needle)
    return "".join(result)


def format_file_block(
    file_path: Path,
    metadata: dict | None,
    lines: list[str],
    matches: list[Match],
    context: int = 2,
    color: bool = False,
    pattern: str = "",
) -> str:
    """Render one file's matches with surrounding context.

    Args:
        file_path: source file (rendered in the header).
        metadata: parsed frontmatter, or None.
        lines: every line of the file (1-based indexing via `lines[lineno - 1]`).
        matches: matching lines (line numbers are 1-based, source-relative).
        context: number of context lines to show before/after each match.
        color: if True, highlight the matched pattern with ANSI codes.
        pattern: the search pattern, used to locate the segment to highlight.

    Returns:
        A multi-line string: header, then context blocks separated by `--`.
        Overlapping context windows are merged (no duplicated lines).
    """
    match_linenos = {m.lineno for m in matches}
    windows = _merge_windows([m.lineno for m in matches], context, len(lines))

    rendered = [_format_header(file_path, metadata)]
    for block_index, (start, end) in enumerate(windows):
        if block_index > 0:
            rendered.append("--")
        for lineno in range(start, end + 1):
            line = lines[lineno - 1]
            is_match = lineno in match_linenos
            if is_match and color:
                line = _highlight(line, pattern)
            separator = ":" if is_match else "-"
            rendered.append(f"  {lineno}{separator} {line}")
    return "\n".join(rendered)


def format_summary(match_count: int, file_count: int) -> str:
    """Render the trailing summary line, e.g. `3 matches in 2 files`."""
    match_word = "match" if match_count == 1 else "matches"
    file_word = "file" if file_count == 1 else "files"
    return f"{match_count} {match_word} in {file_count} {file_word}"
