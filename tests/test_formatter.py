"""Phase 2 unit tests: enriched output formatting contract."""

from __future__ import annotations

from pathlib import Path

from memgrep.formatter import format_file_block, format_summary
from memgrep.matcher import Match

ESC = "\x1b"


def _block(content: str, matches: list[Match], **kwargs) -> str:
    """Helper: format a file block from raw content (splits into lines)."""
    metadata = kwargs.pop("metadata", None)
    return format_file_block(
        Path("/fake/proj/memory/note.md"),
        metadata,
        content.splitlines(),
        matches,
        **kwargs,
    )


def test_header_with_name_and_type():
    out = _block("a\nb\n", [Match(1, "a")], metadata={"name": "x", "type": "user"})
    header = out.splitlines()[0]
    assert header == "/fake/proj/memory/note.md  [name: x | type: user]"


def test_header_without_frontmatter_has_no_brackets():
    out = _block("a\nb\n", [Match(1, "a")], metadata=None)
    header = out.splitlines()[0]
    assert header == "/fake/proj/memory/note.md"
    assert "[" not in header


def test_header_with_type_only():
    out = _block("a\nb\n", [Match(1, "a")], metadata={"type": "user"})
    header = out.splitlines()[0]
    assert header == "/fake/proj/memory/note.md  [type: user]"


def test_match_line_uses_colon_context_uses_dash():
    content = "l1\nl2\nMATCH\nl4\nl5\n"
    out = _block(content, [Match(3, "MATCH")], context=2)
    body = out.splitlines()[1:]
    assert "  3: MATCH" in body
    # Context lines around line 3: lines 1,2,4,5 with dash separator.
    assert "  2- l2" in body
    assert "  4- l4" in body


def test_context_clamped_at_file_boundaries():
    content = "MATCH\nl2\nl3\n"
    out = _block(content, [Match(1, "MATCH")], context=2)
    body = out.splitlines()[1:]
    # No line 0 or negative; first emitted line is line 1.
    assert body[0] == "  1: MATCH"
    assert "  2- l2" in body
    assert "  3- l3" in body
    # Only 3 body lines (file has 3 lines, no phantom line 4/0).
    assert len(body) == 3


def test_overlapping_windows_are_merged_no_duplicates():
    # Matches on lines 3 and 5, context=2 -> windows [1..5] and [3..7] merge.
    content = "l1\nl2\nM3\nl4\nM5\nl6\nl7\n"
    out = _block(content, [Match(3, "M3"), Match(5, "M5")], context=2)
    body = out.splitlines()[1:]
    # One continuous block, no '--' separator, no duplicated lines.
    assert "--" not in body
    linenos = [line[:5].strip().rstrip(":-") for line in body]
    assert linenos == ["1", "2", "3", "4", "5", "6", "7"]


def test_disjoint_windows_separated_by_dashes():
    # Matches on lines 2 and 10, context=1 -> windows [1..3] and [9..11] disjoint.
    content = "\n".join(f"l{i}" for i in range(1, 13)) + "\n"
    out = _block(content, [Match(2, "l2"), Match(10, "l10")], context=1)
    body = out.splitlines()[1:]
    assert "--" in body


def test_no_color_emits_no_ansi():
    out = _block("MATCH here\n", [Match(1, "MATCH here")], color=False, pattern="MATCH")
    assert ESC not in out


def test_color_wraps_matched_segment_in_ansi():
    out = _block("MATCH here\n", [Match(1, "MATCH here")], color=True, pattern="MATCH")
    assert ESC in out
    # The literal matched text is still present (not destroyed by coloring).
    assert "here" in out


def test_summary_singular_and_plural():
    assert format_summary(1, 1) == "1 match in 1 file"
    assert format_summary(3, 2) == "3 matches in 2 files"
