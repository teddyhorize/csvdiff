"""Tests for csvdiff.filter module."""

import pytest
from csvdiff.filter import FilterOptions, FilterError, filter_columns, filter_rows, apply_filters


SAMPLE = [
    {"id": "1", "name": "Alice", "age": "30"},
    {"id": "2", "name": "Bob",   "age": "25"},
    {"id": "3", "name": "Carol", "age": "28"},
]


def test_filter_columns_include():
    opts = FilterOptions(columns=["id", "name"])
    result = filter_columns(SAMPLE, opts)
    assert result == [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}, {"id": "3", "name": "Carol"}]


def test_filter_columns_exclude():
    opts = FilterOptionsndef test_filter_columns_unknown_raises():
    opts = FilterOptions(columns=["id", "nonexistent"])
    with():
    opts = FilterOptions(columns=["id"])
    assert filter_columns([], opts) == []


def test_filter_rows_limit():
    opts = FilterOptions(row_limit=2)
    result = filter_rows(SAMPLE, opts)
    assert len(result) == 2


def test_filter_rows_no_limit():
    opts = FilterOptions()
    result = filter_rows(SAMPLE, opts)
    assert len(result) == 3


def test_apply_filters_combined():
    opts = FilterOptions(columns=["id", "name"], row_limit=2)
    result = apply_filters(SAMPLE, opts)
    assert len(result) == 2
    assert all("age" not in row for row in result)


def test_apply_filters_no_options():
    opts = FilterOptions()
    result = apply_filters(SAMPLE, opts)
    assert result == SAMPLE
