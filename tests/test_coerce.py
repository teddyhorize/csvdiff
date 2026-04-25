"""Tests for csvdiff.coerce."""

import pytest

from csvdiff.coerce import (
    CoerceError,
    CoerceOptions,
    build_coerce_options,
    coerce_row,
    coerce_rows,
)


@pytest.fixture
def row():
    return {"name": "Alice", "age": "30", "score": "9.5", "active": "true"}


def test_coerce_int_column(row):
    opts = CoerceOptions(rules={"age": "int"})
    result = coerce_row(row, opts)
    assert result["age"] == 30
    assert isinstance(result["age"], int)


def test_coerce_float_column(row):
    opts = CoerceOptions(rules={"score": "float"})
    result = coerce_row(row, opts)
    assert result["score"] == pytest.approx(9.5)
    assert isinstance(result["score"], float)


def test_coerce_bool_true(row):
    opts = CoerceOptions(rules={"active": "bool"})
    result = coerce_row(row, opts)
    assert result["active"] is True


def test_coerce_bool_false():
    r = {"flag": "no"}
    opts = CoerceOptions(rules={"flag": "bool"})
    result = coerce_row(r, opts)
    assert result["flag"] is False


def test_coerce_str_is_noop(row):
    opts = CoerceOptions(rules={"name": "str"})
    result = coerce_row(row, opts)
    assert result["name"] == "Alice"


def test_coerce_missing_column_skipped(row):
    opts = CoerceOptions(rules={"nonexistent": "int"})
    result = coerce_row(row, opts)
    assert "nonexistent" not in result


def test_coerce_on_error_skip_leaves_original():
    r = {"age": "not_a_number"}
    opts = CoerceOptions(rules={"age": "int"}, on_error="skip")
    result = coerce_row(r, opts)
    assert result["age"] == "not_a_number"


def test_coerce_on_error_null_sets_none():
    r = {"age": "not_a_number"}
    opts = CoerceOptions(rules={"age": "int"}, on_error="null")
    result = coerce_row(r, opts)
    assert result["age"] is None


def test_coerce_on_error_raise_raises():
    r = {"age": "not_a_number"}
    opts = CoerceOptions(rules={"age": "int"}, on_error="raise")
    with pytest.raises(CoerceError, match="age"):
        coerce_row(r, opts)


def test_coerce_rows_applies_to_all():
    rows = [{"val": "1"}, {"val": "2"}, {"val": "3"}]
    opts = CoerceOptions(rules={"val": "int"})
    results = coerce_rows(rows, opts)
    assert [r["val"] for r in results] == [1, 2, 3]


def test_coerce_rows_empty_list():
    opts = CoerceOptions(rules={"val": "int"})
    assert coerce_rows([], opts) == []


def test_build_coerce_options_defaults():
    opts = build_coerce_options()
    assert opts.rules == {}
    assert opts.on_error == "skip"


def test_build_coerce_options_with_rules():
    opts = build_coerce_options(rules={"age": "int"}, on_error="null")
    assert opts.rules == {"age": "int"}
    assert opts.on_error == "null"


def test_build_coerce_options_invalid_on_error():
    with pytest.raises(CoerceError, match="on_error"):
        build_coerce_options(on_error="explode")


def test_unknown_target_type_raises():
    r = {"col": "value"}
    opts = CoerceOptions(rules={"col": "datetime"}, on_error="raise")
    with pytest.raises(CoerceError, match="Unknown target type"):
        coerce_row(r, opts)
