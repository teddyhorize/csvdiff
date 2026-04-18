"""Tests for csvdiff.normalize."""

import pytest
from csvdiff.normalize import (
    NormalizeOptions,
    NormalizeError,
    normalize_row,
    normalize_rows,
    normalize_options_from_args,
)


@pytest.fixture
def row():
    return {"name": "  Alice ", "city": "  New York ", "age": " 30 "}


def test_strip_whitespace_default(row):
    opts = NormalizeOptions()
    result = normalize_row(row, opts)
    assert result["name"] == "Alice"
    assert result["city"] == "New York"
    assert result["age"] == "30"


def test_no_strip(row):
    opts = NormalizeOptions(strip_whitespace=False)
    result = normalize_row(row, opts)
    assert result["name"] == "  Alice "


def test_lowercase(row):
    opts = NormalizeOptions(lowercase=True)
    result = normalize_row(row, opts)
    assert result["name"] == "alice"
    assert result["city"] == "new york"


def test_targeted_columns(row):
    opts = NormalizeOptions(columns=["name"])
    result = normalize_row(row, opts)
    assert result["name"] == "Alice"
    assert result["city"] == "  New York "  # untouched


def test_normalize_rows_multiple():
    rows = [
        {"a": " x ", "b": " Y "},
        {"a": " z ", "b": " W "},
    ]
    opts = NormalizeOptions(lowercase=True)
    result = normalize_rows(rows, opts)
    assert result[0] == {"a": "x", "b": "y"}
    assert result[1] == {"a": "z", "b": "w"}


def test_normalize_rows_empty():
    assert normalize_rows([], NormalizeOptions()) == []


def test_options_from_args():
    class Args:
        no_strip = False
        normalize_lowercase = True
        normalize_columns = ["name", "city"]

    opts = normalize_options_from_args(Args())
    assert opts.strip_whitespace is True
    assert opts.lowercase is True
    assert opts.columns == ["name", "city"]


def test_options_from_args_defaults():
    class Args:
        pass

    opts = normalize_options_from_args(Args())
    assert opts.strip_whitespace is True
    assert opts.lowercase is False
    assert opts.columns == []
