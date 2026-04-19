"""Tests for csvdiff.cast module."""

import pytest
from csvdiff.cast import CastError, CastOptions, cast_row, cast_rows


@pytest.fixture
def row():
    return {"id": "1", "score": "3.14", "active": "true", "name": "Alice"}


def test_cast_int_column(row):
    opts = CastOptions(int_columns=["id"])
    result = cast_row(row, opts)
    assert result["id"] == 1
    assert isinstance(result["id"], int)


def test_cast_float_column(row):
    opts = CastOptions(float_columns=["score"])
    result = cast_row(row, opts)
    assert result["score"] == pytest.approx(3.14)
    assert isinstance(result["score"], float)


def test_cast_bool_true(row):
    opts = CastOptions(bool_columns=["active"])
    result = cast_row(row, opts)
    assert result["active"] is True


def test_cast_bool_false():
    opts = CastOptions(bool_columns=["active"])
    result = cast_row({"active": "no"}, opts)
    assert result["active"] is False


def test_cast_missing_column_is_skipped(row):
    opts = CastOptions(int_columns=["nonexistent"])
    result = cast_row(row, opts)
    assert result == row


def test_cast_invalid_not_strict(row):
    opts = CastOptions(int_columns=["name"], strict=False)
    result = cast_row(row, opts)
    assert result["name"] == "Alice"  # unchanged


def test_cast_invalid_strict_raises(row):
    opts = CastOptions(int_columns=["name"], strict=True)
    with pytest.raises(CastError, match="name"):
        cast_row(row, opts)


def test_cast_rows_none_options(row):
    result = cast_rows([row], options=None)
    assert result == [row]


def test_cast_rows_applies_to_all():
    rows = [{"x": "1"}, {"x": "2"}, {"x": "3"}]
    opts = CastOptions(int_columns=["x"])
    result = cast_rows(rows, opts)
    assert all(isinstance(r["x"], int) for r in result)
    assert [r["x"] for r in result] == [1, 2, 3]


def test_cast_bool_case_insensitive():
    opts = CastOptions(bool_columns=["flag"])
    assert cast_row({"flag": "TRUE"}, opts)["flag"] is True
    assert cast_row({"flag": "False"}, opts)["flag"] is False
    assert cast_row({"flag": "YES"}, opts)["flag"] is True
