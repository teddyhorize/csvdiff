"""Tests for csvdiff.baseline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from csvdiff.baseline import (
    BaselineError,
    BaselineComparison,
    compare_to_baseline,
    format_baseline_comparison,
    save_baseline,
    load_baseline,
    _diff_to_dict,
)
from csvdiff.differ import DiffResult


def _make_result(
    added=None, removed=None, modified=None, added_cols=None, removed_cols=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
        added_columns=added_cols or [],
        removed_columns=removed_cols or [],
    )


@pytest.fixture()
def simple_result():
    return _make_result(
        added=[{"id": "1", "val": "a"}],
        removed=[{"id": "2", "val": "b"}],
        modified=[("3", {"id": "3", "val": "old"}, {"id": "3", "val": "new"})],
    )


def test_diff_to_dict_keys(simple_result):
    d = _diff_to_dict(simple_result)
    assert set(d.keys()) == {"added", "removed", "modified"}


def test_diff_to_dict_added(simple_result):
    d = _diff_to_dict(simple_result)
    assert d["added"] == [{"id": "1", "val": "a"}]


def test_diff_to_dict_modified_structure(simple_result):
    d = _diff_to_dict(simple_result)
    assert d["modified"][0]["key"] == "3"
    assert d["modified"][0]["old"] == {"id": "3", "val": "old"}
    assert d["modified"][0]["new"] == {"id": "3", "val": "new"}


def test_save_and_load_roundtrip(tmp_path, simple_result):
    p = tmp_path / "baseline.json"
    save_baseline(simple_result, p)
    loaded = load_baseline(p)
    assert loaded["added"] == [{"id": "1", "val": "a"}]
    assert loaded["removed"] == [{"id": "2", "val": "b"}]


def test_load_missing_raises(tmp_path):
    with pytest.raises(BaselineError, match="not found"):
        load_baseline(tmp_path / "nope.json")


def test_compare_identical_is_clean(tmp_path, simple_result):
    p = tmp_path / "baseline.json"
    save_baseline(simple_result, p)
    cmp = compare_to_baseline(simple_result, p)
    assert cmp.is_clean
    assert cmp.new_regressions == []
    assert len(cmp.unchanged_issues) > 0


def test_compare_detects_new_regression(tmp_path):
    baseline_result = _make_result(added=[{"id": "1", "val": "a"}])
    current_result = _make_result(
        added=[{"id": "1", "val": "a"}, {"id": "99", "val": "z"}]
    )
    p = tmp_path / "baseline.json"
    save_baseline(baseline_result, p)
    cmp = compare_to_baseline(current_result, p)
    assert not cmp.is_clean
    assert len(cmp.new_regressions) == 1


def test_compare_detects_resolved(tmp_path):
    baseline_result = _make_result(removed=[{"id": "2", "val": "b"}])
    current_result = _make_result()
    p = tmp_path / "baseline.json"
    save_baseline(baseline_result, p)
    cmp = compare_to_baseline(current_result, p)
    assert cmp.is_clean
    assert len(cmp.resolved_issues) == 1


def test_format_baseline_comparison_clean():
    cmp = BaselineComparison(new_regressions=[], resolved_issues=[], unchanged_issues=[])
    out = format_baseline_comparison(cmp)
    assert "New regressions : 0" in out


def test_format_baseline_comparison_shows_regressions():
    cmp = BaselineComparison(
        new_regressions=['{"id": "5"}'], resolved_issues=[], unchanged_issues=[]
    )
    out = format_baseline_comparison(cmp)
    assert "New regressions:" in out
    assert '{"id": "5"}' in out
