"""Tests for csvdiff.differ module."""

import pytest
from csvdiff.differ import diff_csv, DiffResult


LEFT = [
    {"id": "1", "name": "Alice", "age": "30"},
    {"id": "2", "name": "Bob", "age": "25"},
    {"id": "3", "name": "Carol", "age": "28"},
]

RIGHT = [
    {"id": "1", "name": "Alice", "age": "31"},
    {"id": "2", "name": "Bob", "age": "25"},
    {"id": "4", "name": "Dave", "age": "22"},
]


def test_no_differences():
    result = diff_csv(LEFT[:2], LEFT[:2], key="id")
    assert not result.has_differences


def test_added_rows_by_key():
    result = diff_csv(LEFT, RIGHT, key="id")
    assert len(result.added_rows) == 1
    assert result.added_rows[0]["id"] == "4"


def test_removed_rows_by_key():
    result = diff_csv(LEFT, RIGHT, key="id")
    assert len(result.removed_rows) == 1
    assert result.removed_rows[0]["id"] == "3"


def test_modified_rows_by_key():
    result = diff_csv(LEFT, RIGHT, key="id")
    assert len(result.modified_rows) == 1
    assert "age" in result.modified_rows[0]
    assert result.modified_rows[0]["age"] == ("30", "31")


def test_added_columns():
    right_extra = [{**row, "email": "x@x.com"} for row in RIGHT]
    result = diff_csv(LEFT, right_extra, key="id")
    assert "email" in result.added_columns


def test_removed_columns():
    right_fewer = [{"id": row["id"], "name": row["name"]} for row in RIGHT]
    result = diff_csv(LEFT, right_fewer, key="id")
    assert "age" in result.removed_columns


def test_diff_by_index_added_removed():
    result = diff_csv(LEFT, RIGHT)  # no key
    assert len(result.added_rows) == 0
    assert len(result.removed_rows) == 0


def test_diff_by_index_modifications():
    result = diff_csv(LEFT, RIGHT)
    # row 0: age 30 vs 31, row 2: id/name/age differ
    assert len(result.modified_rows) >= 1


def test_empty_inputs():
    result = diff_csv([], [])
    assert not result.has_differences
