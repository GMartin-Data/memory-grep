"""Substring matching with ripgrep-style smart-case."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Match:
    lineno: int
    line: str


def is_smart_case_insensitive(pattern: str) -> bool:
    """Return True if pattern is fully lowercase (smart-case insensitive)."""
    return pattern == pattern.lower()


def find_matches(content: str, pattern: str) -> list[Match]:
    """Return all matches of `pattern` in `content` (one entry per matching line).

    Smart-case: case-insensitive if pattern is all-lowercase, sensitive otherwise.
    """
    if not pattern:
        return []

    insensitive = is_smart_case_insensitive(pattern)
    needle = pattern.lower() if insensitive else pattern

    matches: list[Match] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        haystack = line.lower() if insensitive else line
        if needle in haystack:
            matches.append(Match(lineno=lineno, line=line))
    return matches
