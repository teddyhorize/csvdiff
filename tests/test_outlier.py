"""Tests for csvdiff.outlier."""
from __future__ import annotations

import pytest

from csvdiff.outlier import (
    OutlierError,
    OutlierResult,
    detect_outliers,
    format_outlier,
)


@pytest.fixture
def rows():
    return [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "12"},
        {"name": "c", "score": "11"},
        {"name": "d", "score": "13"},
        {"name": "e", "score": "100"},  # outlier
    ]


def test_detect_outliers_returns_result(rows):
    result = detect_outliers(rows, column="score")
    assert isinstance(result, OutlierResult)


def test_detect_outliers_finds_outlier(rows):
    result = detect_outliers(rows, column="score")
    assert result.count == 1
    assert result.outliers[0]["name"] == "e"


def test_detect_outliers_no_outlier():
    rows = [
        {"x": "1"}, {"x": "2"}, {"x": "3"}, {"x": "2"}, {"x": "1"},
    ]
    result = detect_outliers(rows, column="x", z_threshold=2.5)
    assert result.count == 0


def test_detect_outliers_zero_stdev():
    rows = [{"v": "5"}, {"v": "5"}, {"v": "5"}]
    result = detect_outliers(rows, column="v")
    assert result.stdev == 0.0
    assert result.count == 0


def test_detect_outliers_missing_column(rows):
    with pytest.raises(OutlierError, match="not found"):
        detect_outliers(rows, column="nonexistent")


def test_detect_outliers_empty_rows():
    with pytest.raises(OutlierError, match="No rows"):
        detect_outliers([], column="score")


def test_detect_outliers_too_few_numeric():
    rows = [{"v": "abc"}, {"v": "1"}]
    with pytest.raises(OutlierError, match="fewer than 2"):
        detect_outliers(rows, column="v")


def test_detect_outliers_skips_non_numeric(rows):
    rows_with_blank = rows + [{"name": "f", "score": "n/a"}]
    result = detect_outliers(rows_with_blank, column="score")
    # non-numeric row ignored; outlier still found
    assert result.count == 1


def test_result_mean_approx(rows):
    result = detect_outliers(rows, column="score")
    assert result.mean == pytest.approx((10 + 12 + 11 + 13 + 100) / 5)


def test_format_outlier_contains_column(rows):
    result = detect_outliers(rows, column="score")
    text = format_outlier(result)
    assert "score" in text
    assert "1 found" in text


def test_format_outlier_color_wraps_ansi(rows):
    result = detect_outliers(rows, column="score")
    text = format_outlier(result, color=True)
    assert "\033[33m" in text


def test_format_outlier_no_outliers_no_rows():
    rows = [{"v": "1"}, {"v": "2"}, {"v": "3"}]
    result = detect_outliers(rows, column="v")
    text = format_outlier(result)
    assert "0 found" in text
