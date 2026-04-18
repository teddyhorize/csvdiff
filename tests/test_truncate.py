"""Tests for csvdiff.truncate module."""

import pytest
from csvdiff.truncate import (
    TruncateError,
    TruncateOptions,
    truncate_cell,
    truncate_rows,
    truncate_columns,
    apply_truncation,
)

ROWS = [
    {"id": "1", "name": "Alice", "note": "hello world"},
    {"id": "2", "name": "Bob",   "note": "foo bar baz"},
    {"id": "3", "name": "Carol", "note": "x"},
]
COLS = ["id", "name", "note"]


def test_truncate_cell_no_limit():
    assert truncate_cell("hello", 0) == "hello"


def test_truncate_cell_within_limit():
    assert truncate_cell("hello", 10) == "hello"


def test_truncate_cell_exceeds_limit():
    assert truncate_cell("hello world", 5) == "hello..."


def test_truncate_rows_no_limit():
    assert truncate_rows(ROWS, 0) == ROWS


def test_truncate_rows_limits_count():
    result = truncate_rows(ROWS, 2)
    assert len(result) == 2
    assert result[0]["id"] == "1"


def test_truncate_columns_no_limit():
    result = truncate_columns(ROWS, COLS, 0)
    assert all("note" in r for r in result)


def test_truncate_columns_limits():
    result = truncate_columns(ROWS, COLS, 2)
    assert all("note" not in r for r in result)
    assert all("id" in r and "name" in r for r in result)


def test_apply_truncation_combined():
    opts = TruncateOptions(max_rows=2, max_cols=2, max_cell_len=3)
    result = apply_truncation(ROWS, COLS, opts)
    assert len(result) == 2
    assert "note" not in result[0]
    assert result[0]["name"] == "Ali..."


def test_apply_truncation_negative_raises():
    opts = TruncateOptions(max_rows=-1)
    with pytest.raises(TruncateError):
        apply_truncation(ROWS, COLS, opts)


def test_apply_truncation_empty_rows():
    opts = TruncateOptions(max_rows=5, max_cols=2)
    assert apply_truncation([], COLS, opts) == []
