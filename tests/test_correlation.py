"""Tests for csvdiff.correlation."""
import pytest
from csvdiff.correlation import (
    CorrelationError,
    CorrelationResult,
    _pearson,
    compute_correlation,
    format_correlation,
)


@pytest.fixture
def rows():
    return [
        {"x": "1", "y": "2", "z": "5"},
        {"x": "2", "y": "4", "z": "4"},
        {"x": "3", "y": "6", "z": "3"},
        {"x": "4", "y": "8", "z": "2"},
        {"x": "5", "y": "10", "z": "1"},
    ]


def test_pearson_perfect_positive():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [2.0, 4.0, 6.0, 8.0, 10.0]
    r = _pearson(xs, ys)
    assert r is not None
    assert abs(r - 1.0) < 1e-9


def test_pearson_perfect_negative():
    xs = [1.0, 2.0, 3.0]
    ys = [3.0, 2.0, 1.0]
    r = _pearson(xs, ys)
    assert r is not None
    assert abs(r - (-1.0)) < 1e-9


def test_pearson_too_few_points():
    assert _pearson([1.0], [1.0]) is None


def test_pearson_zero_variance_returns_none():
    assert _pearson([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) is None


def test_compute_correlation_empty_raises():
    with pytest.raises(CorrelationError, match="empty"):
        compute_correlation([])


def test_compute_correlation_missing_column_raises(rows):
    with pytest.raises(CorrelationError, match="not found"):
        compute_correlation(rows, columns=["x", "missing"])


def test_compute_correlation_returns_result(rows):
    result = compute_correlation(rows, columns=["x", "y"])
    assert isinstance(result, CorrelationResult)
    assert "x" in result.columns
    assert "y" in result.columns


def test_compute_correlation_x_y_positive(rows):
    result = compute_correlation(rows, columns=["x", "y"])
    r = result.get("x", "y")
    assert r is not None
    assert abs(r - 1.0) < 1e-9


def test_compute_correlation_x_z_negative(rows):
    result = compute_correlation(rows, columns=["x", "z"])
    r = result.get("x", "z")
    assert r is not None
    assert r < 0


def test_compute_correlation_self_is_one(rows):
    result = compute_correlation(rows, columns=["x", "y"])
    r = result.get("x", "x")
    assert r is not None
    assert abs(r - 1.0) < 1e-9


def test_compute_correlation_all_columns(rows):
    result = compute_correlation(rows)
    assert set(result.columns) == {"x", "y", "z"}


def test_format_correlation_returns_string(rows):
    result = compute_correlation(rows, columns=["x", "y"])
    text = format_correlation(result)
    assert isinstance(text, str)
    assert "x" in text
    assert "y" in text


def test_format_correlation_non_numeric_skipped():
    rows = [
        {"a": "hello", "b": "1"},
        {"a": "world", "b": "2"},
    ]
    result = compute_correlation(rows, columns=["a", "b"])
    r = result.get("a", "b")
    assert r is None
