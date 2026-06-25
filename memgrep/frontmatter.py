"""YAML frontmatter parsing for memory files."""

from __future__ import annotations

import yaml

FRONTMATTER_DELIMITER = "---"


class InvalidFrontmatterError(Exception):
    """Raised when frontmatter delimiters are present but YAML is malformed."""


def parse_frontmatter(content: str) -> tuple[dict | None, str, int]:
    """Split a memory file into (metadata, body, body_offset).

    Returns:
        metadata: parsed YAML dict, or `None` if no frontmatter is present.
        body: file content after the closing delimiter (or full content if no
            frontmatter).
        body_offset: 1-based line number of the first body line in the original
            content. Used to remap match line numbers back to the source file.

    Raises:
        InvalidFrontmatterError: if a frontmatter block is opened but cannot be
            parsed as YAML, or yields a non-mapping value.
    """
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n") != FRONTMATTER_DELIMITER:
        return None, content, 1

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].rstrip("\n") == FRONTMATTER_DELIMITER:
            closing_index = index
            break

    if closing_index is None:
        raise InvalidFrontmatterError("missing closing '---' delimiter")

    yaml_block = "".join(lines[1:closing_index])
    try:
        metadata = yaml.safe_load(yaml_block) or {}
    except yaml.YAMLError as exc:
        raise InvalidFrontmatterError(str(exc)) from exc

    if not isinstance(metadata, dict):
        raise InvalidFrontmatterError("frontmatter is not a mapping")

    body = "".join(lines[closing_index + 1 :])
    body_offset = closing_index + 2
    return metadata, body, body_offset
