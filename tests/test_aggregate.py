"""Tests for csvdiff.aggregate."""
import pytest

from csvdiff.aggregate import (
    AggregateError,
    AggregateOptions,
    AggregateResult,
    aggregate_column,
    aggregate_diff,
    format_aggregate,
)
from csvdiff.differ import DiffResult


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[
            {"id": "1", "value": "10.0", "label": "a"},
            {"id": "2", "value": "20.0", "label": "b"},
        ],
        removed=[
            {"id": "3", "value": "5.0", "label": "c"},
        ],
        modified=[
            (
                {"id": "4", "value": "1.0", "label": "d"},
                {"id": "4", "value": "99.0", "label": "D"},
            )
        ],
        unchanged=[],
    )


def test_aggregate_column_counts_values(result):
    opts = AggregateOptions(columns=["value"])
    r = aggregate_column(result, "value", opts)
    assert r.count == 4  # 2 added + 1 removed + 1 modified-new


def test_aggregate_column_sum(result):
    opts = AggregateOptions(columns=["value"])
    r = aggregate_column(result, "value", opts)
    assert r.total == pytest.approx(10.0 + 20.0 + 5.0 + 99.0)


def test_aggregate_column_min_max(result):
    opts = AggregateOptions(columns=["value"])
    r = aggregate_column(result, "value", opts)
    assert r.minimum == pytest.approx(5.0)
    assert r.maximum == pytest.approx(99.0)


def test_aggregate_column_mean(result):
    opts = AggregateOptions(columns=["value"])
    r = aggregate_column(result, "value", opts)
    expected_mean = (10.0 + 20.0 + 5.0 + 99.0) / 4
    assert r.mean == pytest.approx(expected_mean)


def test_aggregate_excludes_added(result):
    opts = AggregateOptions(columns=["value"], include_added=False)
    r = aggregate_column(result, "value", opts)
    assert r.count == 2  # 1 removed + 1 modified-new


def test_aggregate_excludes_removed(result):
    opts = AggregateOptions(columns=["value"], include_removed=False)
    r = aggregate_column(result, "value", opts)
    assert r.count == 3  # 2 added + 1 modified-new


def test_aggregate_non_numeric_skipped(result):
    opts = AggregateOptions(columns=["label"])
    r = aggregate_column(result, "label", opts)
    assert r.count == 0
    assert r.minimum is None
    assert r.mean is None


def test_aggregate_diff_no_columns_raises(result):
    opts = AggregateOptions(columns=[])
    with pytest.raises(AggregateError):
        aggregate_diff(result, opts)


def test_aggregate_diff_returns_one_per_column(result):
    opts = AggregateOptions(columns=["value", "label"])
    results = aggregate_diff(result, opts)
    assert len(results) == 2
    assert results[0].column == "value"
    assert results[1].column == "label"


def test_format_aggregate_empty():
    assert format_aggregate([]) == "No aggregation results."


def test_format_aggregate_contains_column_name(result):
    opts = AggregateOptions(columns=["value"])
    results = aggregate_diff(result, opts)
    output = format_aggregate(results)
    assert "value" in output
    assert "count=" in output
    assert "sum=" in output
