"""Tests for csvdiff.frequency."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult
from csvdiff.frequency import (
    ColumnFrequency,
    FrequencyError,
    FrequencyResult,
    compute_frequency,
    format_frequency,
)


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[
            {"id": "1", "status": "active", "region": "EU"},
            {"id": "2", "status": "active", "region": "US"},
        ],
        removed=[
            {"id": "3", "status": "inactive", "region": "EU"},
        ],
        modified=[
            {"new": {"id": "4", "status": "active", "region": "APAC"},
             "old": {"id": "4", "status": "inactive", "region": "APAC"}},
        ],
        unchanged=[
            {"id": "5", "status": "inactive", "region": "US"},
        ],
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def test_compute_frequency_returns_result(result):
    freq = compute_frequency(result)
    assert isinstance(freq, FrequencyResult)


def test_compute_frequency_column_names(result):
    freq = compute_frequency(result)
    names = [cf.column for cf in freq.columns]
    assert "status" in names
    assert "region" in names


def test_compute_frequency_counts_added_and_removed(result):
    freq = compute_frequency(result)
    status_cf = freq.get("status")
    assert status_cf is not None
    # added: active x2, removed: inactive x1, modified new: active x1
    assert status_cf.counts.get("active") == 3
    assert status_cf.counts.get("inactive") == 1


def test_compute_frequency_excludes_unchanged_by_default(result):
    freq = compute_frequency(result)
    region_cf = freq.get("region")
    # unchanged row has region=US; should not appear unless include_unchanged=True
    # added: EU, US; removed: EU; modified new: APAC  => US=1
    assert region_cf.counts.get("US") == 1


def test_compute_frequency_includes_unchanged_when_flag_set(result):
    freq = compute_frequency(result, include_unchanged=True)
    region_cf = freq.get("region")
    # US appears in added (1) + unchanged (1) = 2
    assert region_cf.counts.get("US") == 2


def test_compute_frequency_subset_of_columns(result):
    freq = compute_frequency(result, columns=["status"])
    assert len(freq.columns) == 1
    assert freq.columns[0].column == "status"


def test_compute_frequency_unknown_column_raises(result):
    with pytest.raises(FrequencyError, match="Unknown columns"):
        compute_frequency(result, columns=["nonexistent"])


def test_compute_frequency_empty_result(empty_result):
    freq = compute_frequency(empty_result)
    assert freq.columns == []


def test_column_frequency_total(result):
    freq = compute_frequency(result)
    status_cf = freq.get("status")
    assert status_cf.total == 4  # 2 added + 1 removed + 1 modified


def test_column_frequency_unique(result):
    freq = compute_frequency(result)
    status_cf = freq.get("status")
    assert status_cf.unique == 2  # active, inactive


def test_column_frequency_top(result):
    freq = compute_frequency(result)
    status_cf = freq.get("status")
    top = status_cf.top(1)
    assert top[0][0] == "active"
    assert top[0][1] == 3


def test_format_frequency_empty():
    freq = FrequencyResult()
    out = format_frequency(freq)
    assert "No frequency data" in out


def test_format_frequency_contains_column_name(result):
    freq = compute_frequency(result)
    out = format_frequency(freq)
    assert "status" in out
    assert "region" in out


def test_format_frequency_shows_counts(result):
    freq = compute_frequency(result)
    out = format_frequency(freq)
    assert "active" in out
