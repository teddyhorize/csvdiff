"""Tests for csvdiff.quantile."""

import pytest

from csvdiff.quantile import (
    ColumnQuantiles,
    QuantileError,
    QuantileResult,
    compute_quantiles,
    format_quantiles,
)


@pytest.fixture()
def rows():
    return [
        {"name": "alice", "score": "10", "age": "30"},
        {"name": "bob",   "score": "20", "age": "25"},
        {"name": "carol", "score": "30", "age": "35"},
        {"name": "dave",  "score": "40", "age": "28"},
    ]


def test_compute_quantiles_empty():
    result = compute_quantiles([])
    assert isinstance(result, QuantileResult)
    assert result.columns == {}


def test_compute_quantiles_column_names(rows):
    result = compute_quantiles(rows, columns=["score"])
    assert "score" in result.columns


def test_compute_quantiles_count(rows):
    result = compute_quantiles(rows, columns=["score"])
    assert result.columns["score"].count == 4


def test_compute_quantiles_min_max(rows):
    q = compute_quantiles(rows, columns=["score"]).columns["score"]
    assert q.min == 10.0
    assert q.max == 40.0


def test_compute_quantiles_median(rows):
    q = compute_quantiles(rows, columns=["score"]).columns["score"]
    # median of [10, 20, 30, 40] via linear interpolation at 50th pct
    assert q.median == pytest.approx(25.0)


def test_compute_quantiles_q1_q3(rows):
    q = compute_quantiles(rows, columns=["score"]).columns["score"]
    assert q.q1 == pytest.approx(17.5)
    assert q.q3 == pytest.approx(32.5)


def test_compute_quantiles_iqr(rows):
    q = compute_quantiles(rows, columns=["score"]).columns["score"]
    assert q.iqr() == pytest.approx(15.0)


def test_compute_quantiles_all_columns_default(rows):
    result = compute_quantiles(rows)
    assert "score" in result.columns
    assert "age" in result.columns
    # 'name' has no numeric data
    assert result.columns["name"].count == 0


def test_compute_quantiles_non_numeric_column(rows):
    q = compute_quantiles(rows, columns=["name"]).columns["name"]
    assert q.count == 0
    assert q.min is None
    assert q.iqr() is None


def test_compute_quantiles_unknown_column_raises(rows):
    with pytest.raises(QuantileError, match="not found"):
        compute_quantiles(rows, columns=["nonexistent"])


def test_compute_quantiles_single_value():
    rows = [{"v": "42"}]
    q = compute_quantiles(rows, columns=["v"]).columns["v"]
    assert q.min == 42.0
    assert q.max == 42.0
    assert q.median == 42.0


def test_get_returns_column_quantiles(rows):
    result = compute_quantiles(rows, columns=["score"])
    assert isinstance(result.get("score"), ColumnQuantiles)


def test_get_missing_column_returns_none(rows):
    result = compute_quantiles(rows, columns=["score"])
    assert result.get("age") is None


def test_format_quantiles_empty():
    assert format_quantiles(QuantileResult()) == "No quantile data."


def test_format_quantiles_contains_column_name(rows):
    result = compute_quantiles(rows, columns=["score"])
    output = format_quantiles(result)
    assert "score" in output


def test_format_quantiles_non_numeric_label(rows):
    result = compute_quantiles(rows, columns=["name"])
    output = format_quantiles(result)
    assert "no numeric data" in output
