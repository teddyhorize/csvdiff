"""Tests for csvdiff.zscore."""

import math
import pytest

from csvdiff.zscore import (
    ZScoreError,
    ZScoreColumn,
    ZScoreResult,
    compute_zscore,
    normalize_rows,
)


@pytest.fixture()
def rows():
    return [
        {"id": "1", "val": "10", "label": "a"},
        {"id": "2", "val": "20", "label": "b"},
        {"id": "3", "val": "30", "label": "c"},
    ]


def test_compute_zscore_empty():
    result = compute_zscore([])
    assert result.columns == {}


def test_compute_zscore_column_names(rows):
    result = compute_zscore(rows, columns=["val"])
    assert "val" in result.columns


def test_compute_zscore_mean(rows):
    result = compute_zscore(rows, columns=["val"])
    assert math.isclose(result.columns["val"].mean, 20.0)


def test_compute_zscore_stdev(rows):
    result = compute_zscore(rows, columns=["val"])
    # population stdev of [10, 20, 30] = ~8.165
    assert math.isclose(result.columns["val"].stdev, 8.16496580927726, rel_tol=1e-5)


def test_compute_zscore_count(rows):
    result = compute_zscore(rows, columns=["val"])
    assert result.columns["val"].count == 3


def test_compute_zscore_skips_non_numeric(rows):
    result = compute_zscore(rows, columns=["label"])
    assert "label" not in result.columns


def test_compute_zscore_unknown_column_raises(rows):
    with pytest.raises(ZScoreError, match="Column not found"):
        compute_zscore(rows, columns=["missing"])


def test_compute_zscore_all_columns_by_default(rows):
    result = compute_zscore(rows)
    # 'id' and 'val' are numeric; 'label' is not
    assert "val" in result.columns
    assert "id" in result.columns
    assert "label" not in result.columns


def test_zscore_column_normalize_zero_stdev():
    col = ZScoreColumn(name="x", mean=5.0, stdev=0.0, count=3)
    assert col.normalize(5.0) is None


def test_zscore_column_normalize_value():
    col = ZScoreColumn(name="x", mean=0.0, stdev=1.0, count=3)
    assert math.isclose(col.normalize(1.0), 1.0)
    assert math.isclose(col.normalize(-1.0), -1.0)


def test_normalize_rows_adds_suffix(rows):
    result = compute_zscore(rows, columns=["val"])
    normalized = normalize_rows(rows, result)
    assert "val_z" in normalized[0]


def test_normalize_rows_middle_value_is_zero(rows):
    result = compute_zscore(rows, columns=["val"])
    normalized = normalize_rows(rows, result)
    z_middle = float(normalized[1]["val_z"])
    assert math.isclose(z_middle, 0.0, abs_tol=1e-9)


def test_normalize_rows_custom_suffix(rows):
    result = compute_zscore(rows, columns=["val"])
    normalized = normalize_rows(rows, result, suffix="_norm")
    assert "val_norm" in normalized[0]
    assert "val_z" not in normalized[0]


def test_normalize_rows_non_numeric_cell_empty():
    rows = [{"val": "abc"}]
    result = compute_zscore([{"val": "1"}, {"val": "2"}], columns=["val"])
    normalized = normalize_rows(rows, result)
    assert normalized[0]["val_z"] == ""
