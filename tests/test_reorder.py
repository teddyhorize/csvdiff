"""Tests for csvdiff.reorder."""

import pytest
from csvdiff.reorder import (
    ReorderError,
    ReorderOptions,
    reorder_headers,
    reorder_row,
    reorder_rows,
)


HEADERS = ["id", "name", "age", "city"]
ROWS = [
    {"id": "1", "name": "Alice", "age": "30", "city": "NY"},
    {"id": "2", "name": "Bob", "age": "25", "city": "LA"},
]


def test_reorder_headers_explicit_order():
    opts = ReorderOptions(columns=["name", "id", "city", "age"])
    result = reorder_headers(HEADERS, opts)
    assert result == ["name", "id", "city", "age"]


def test_reorder_headers_partial_explicit_appends_rest():
    opts = ReorderOptions(columns=["city", "name"])
    result = reorder_headers(HEADERS, opts)
    assert result[:2] == ["city", "name"]
    assert set(result) == set(HEADERS)


def test_reorder_headers_move_to_front():
    opts = ReorderOptions(move_to_front=["age"])
    result = reorder_headers(HEADERS, opts)
    assert result[0] == "age"
    assert set(result) == set(HEADERS)


def test_reorder_headers_move_to_back():
    opts = ReorderOptions(move_to_back=["id"])
    result = reorder_headers(HEADERS, opts)
    assert result[-1] == "id"
    assert set(result) == set(HEADERS)


def test_reorder_headers_no_options_unchanged():
    opts = ReorderOptions()
    result = reorder_headers(HEADERS, opts)
    assert result == HEADERS


def test_reorder_headers_unknown_column_raises():
    opts = ReorderOptions(columns=["id", "nonexistent"])
    with pytest.raises(ReorderError, match="Unknown columns"):
        reorder_headers(HEADERS, opts)


def test_reorder_headers_unknown_move_to_front_raises():
    opts = ReorderOptions(move_to_front=["ghost"])
    with pytest.raises(ReorderError, match="Unknown column"):
        reorder_headers(HEADERS, opts)


def test_reorder_row_reorders_keys():
    row = {"id": "1", "name": "Alice", "age": "30", "city": "NY"}
    ordered = ["city", "name", "id", "age"]
    result = reorder_row(row, ordered)
    assert list(result.keys()) == ordered


def test_reorder_row_skips_missing_keys():
    row = {"id": "1", "name": "Alice"}
    ordered = ["name", "id", "age"]
    result = reorder_row(row, ordered)
    assert list(result.keys()) == ["name", "id"]


def test_reorder_rows_returns_tuple():
    opts = ReorderOptions(move_to_front=["name"])
    new_headers, new_rows = reorder_rows(ROWS, HEADERS, opts)
    assert new_headers[0] == "name"
    assert all(list(r.keys())[0] == "name" for r in new_rows)


def test_reorder_rows_preserves_values():
    opts = ReorderOptions(columns=["city", "age", "name", "id"])
    _, new_rows = reorder_rows(ROWS, HEADERS, opts)
    assert new_rows[0]["name"] == "Alice"
    assert new_rows[1]["city"] == "LA"
