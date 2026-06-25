"""Phase 1b unit tests: frontmatter parsing contract."""

from __future__ import annotations

import pytest

from memgrep.frontmatter import InvalidFrontmatterError, parse_frontmatter


def test_parses_metadata_body_and_offset():
    content = "---\nname: feedback one\ntype: feedback\n---\nBody line.\n"
    metadata, body, body_offset = parse_frontmatter(content)

    assert metadata == {"name": "feedback one", "type": "feedback"}
    assert body == "Body line.\n"
    # Body starts at line 5 (1:--- 2:name 3:type 4:--- 5:body).
    assert body_offset == 5


def test_no_frontmatter_returns_none_and_full_content():
    content = "Just a plain note.\nNo frontmatter here.\n"
    metadata, body, body_offset = parse_frontmatter(content)

    assert metadata is None
    assert body == content
    assert body_offset == 1


def test_malformed_yaml_raises():
    content = "---\nname: : broken: :\n  bad indent\n---\nBody.\n"
    with pytest.raises(InvalidFrontmatterError):
        parse_frontmatter(content)


def test_missing_closing_delimiter_raises():
    content = "---\nname: orphan\nBody never closes frontmatter.\n"
    with pytest.raises(InvalidFrontmatterError):
        parse_frontmatter(content)


def test_non_mapping_frontmatter_raises():
    content = "---\n- just\n- a\n- list\n---\nBody.\n"
    with pytest.raises(InvalidFrontmatterError):
        parse_frontmatter(content)
