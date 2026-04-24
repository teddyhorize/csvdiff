"""Tests for csvdiff.headermap."""
import pytest

from csvdiff.headermap import (
    HeaderMapError,
    HeaderMapping,
    _normalize,
    build_header_mapping,
    format_header_mapping,
)


# ---------------------------------------------------------------------------
# _normalize
# ---------------------------------------------------------------------------

def test_normalize_lowercases():
    assert _normalize("Name") == "name"


def test_normalize_strips_whitespace():
    assert _normalize("  id  ") == "id"


def test_normalize_replaces_spaces_and_dashes():
    assert _normalize("First Name") == "first_name"
    assert _normalize("last-name") == "last_name"


# ---------------------------------------------------------------------------
# build_header_mapping — exact
# ---------------------------------------------------------------------------

def test_exact_match_recorded():
    m = build_header_mapping(["id", "name"], ["id", "name"])
    assert m.exact == {"id": "id", "name": "name"}
    assert m.fuzzy == {}
    assert m.unmapped_left == []
    assert m.unmapped_right == []


def test_exact_partial_match():
    m = build_header_mapping(["id", "name"], ["id", "age"])
    assert "id" in m.exact
    assert "name" in m.unmapped_left
    assert "age" in m.unmapped_right


# ---------------------------------------------------------------------------
# build_header_mapping — fuzzy
# ---------------------------------------------------------------------------

def test_fuzzy_case_insensitive():
    m = build_header_mapping(["Name"], ["name"], fuzzy=True)
    assert m.fuzzy == {"Name": "name"}
    assert m.unmapped_left == []


def test_fuzzy_normalizes_separators():
    m = build_header_mapping(["First Name"], ["first_name"], fuzzy=True)
    assert "First Name" in m.fuzzy


def test_fuzzy_disabled_leaves_unmapped():
    m = build_header_mapping(["Name"], ["name"], fuzzy=False)
    assert m.fuzzy == {}
    assert "Name" in m.unmapped_left
    assert "name" in m.unmapped_right


def test_invalid_input_raises():
    with pytest.raises(HeaderMapError):
        build_header_mapping("id,name", ["id"])  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# format_header_mapping
# ---------------------------------------------------------------------------

def test_format_empty_headers():
    m = build_header_mapping([], [])
    text = format_header_mapping(m)
    assert text == "No headers to map."


def test_format_shows_exact():
    m = build_header_mapping(["id"], ["id"])
    text = format_header_mapping(m)
    assert "Exact matches" in text
    assert "'id'" in text


def test_format_shows_fuzzy():
    m = build_header_mapping(["Name"], ["name"])
    text = format_header_mapping(m)
    assert "Fuzzy matches" in text


def test_format_shows_unmapped():
    m = build_header_mapping(["x"], ["y"], fuzzy=False)
    text = format_header_mapping(m)
    assert "Unmapped (left)" in text
    assert "Unmapped (right)" in text
