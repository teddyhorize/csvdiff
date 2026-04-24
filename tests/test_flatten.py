"""Tests for csvdiff.flatten."""

import pytest
from csvdiff.flatten import (
    FlattenError,
    FlattenOptions,
    flatten_rows,
    format_flatten,
)


@pytest.fixture
def rows():
    return [
        {"id": "1", "tags": "a|b|c", "name": "Alice"},
        {"id": "2", "tags": "x|y", "name": "Bob"},
        {"id": "3", "tags": "only", "name": "Carol"},
    ]


def test_flatten_basic_count(rows):
    opts = FlattenOptions(column="tags")
    result = flatten_rows(rows, opts)
    assert result.original_count == 3
    assert result.expanded_count == 6


def test_flatten_produces_correct_values(rows):
    opts = FlattenOptions(column="tags")
    result = flatten_rows(rows, opts)
    tag_values = [r["tags"] for r in result.rows]
    assert tag_values == ["a", "b", "c", "x", "y", "only"]


def test_flatten_preserves_other_columns(rows):
    opts = FlattenOptions(column="tags")
    result = flatten_rows(rows, opts)
    first_three = result.rows[:3]
    for r in first_three:
        assert r["id"] == "1"
        assert r["name"] == "Alice"


def test_flatten_strips_whitespace():
    rows = [{"id": "1", "tags": " a | b "}]
    opts = FlattenOptions(column="tags", strip=True)
    result = flatten_rows(rows, opts)
    assert result.rows[0]["tags"] == "a"
    assert result.rows[1]["tags"] == "b"


def test_flatten_no_strip():
    rows = [{"id": "1", "tags": " a | b "}]
    opts = FlattenOptions(column="tags", strip=False)
    result = flatten_rows(rows, opts)
    assert result.rows[0]["tags"] == " a "


def test_flatten_skip_empty_by_default():
    rows = [{"id": "1", "tags": "a||b"}]
    opts = FlattenOptions(column="tags")
    result = flatten_rows(rows, opts)
    assert result.expanded_count == 2
    assert all(r["tags"] != "" for r in result.rows)


def test_flatten_keep_empty():
    rows = [{"id": "1", "tags": "a||b"}]
    opts = FlattenOptions(column="tags", keep_empty=True)
    result = flatten_rows(rows, opts)
    assert result.expanded_count == 3


def test_flatten_custom_separator():
    rows = [{"id": "1", "tags": "a,b,c"}]
    opts = FlattenOptions(column="tags", separator=",")
    result = flatten_rows(rows, opts)
    assert result.expanded_count == 3


def test_flatten_missing_column_raises():
    rows = [{"id": "1", "name": "Alice"}]
    opts = FlattenOptions(column="tags")
    with pytest.raises(FlattenError, match="tags"):
        flatten_rows(rows, opts)


def test_flatten_empty_input():
    result = flatten_rows([], FlattenOptions(column="tags"))
    assert result.original_count == 0
    assert result.expanded_count == 0
    assert result.rows == []


def test_format_flatten_message(rows):
    opts = FlattenOptions(column="tags")
    result = flatten_rows(rows, opts)
    msg = format_flatten(result)
    assert "3" in msg
    assert "6" in msg
