"""Tests for csvdiff.score."""
import pytest
from csvdiff.differ import DiffResult
from csvdiff.score import compute_score, format_score, SimilarityScore


def _make_result(
    added=None, removed=None, modified=None, unchanged=None
) -> DiffResult:
    return DiffResult(
        added=added or {},
        removed=removed or {},
        modified=modified or {},
        unchanged=unchanged or {},
        added_columns=[],
        removed_columns=[],
    )


def test_compute_score_all_unchanged():
    r = _make_result(unchanged={"a": {}, "b": {}})
    s = compute_score(r)
    assert s.score == 1.0
    assert s.matched_rows == 2
    assert s.total_rows == 2


def test_compute_score_all_added():
    r = _make_result(added={"a": {}, "b": {}})
    s = compute_score(r)
    assert s.score == 0.0
    assert s.added == 2


def test_compute_score_mixed():
    r = _make_result(
        unchanged={"a": {}},
        added={"b": {}},
        removed={"c": {}},
        modified={"d": {}},
    )
    s = compute_score(r)
    assert s.total_rows == 4
    assert s.matched_rows == 1
    assert s.score == 0.25


def test_compute_score_empty():
    r = _make_result()
    s = compute_score(r)
    assert s.score == 1.0
    assert s.total_rows == 0


def test_format_score_contains_pct():
    r = _make_result(unchanged={"a": {}}, added={"b": {}})
    s = compute_score(r)
    text = format_score(s)
    assert "50.0%" in text
    assert "Total Rows" in text
    assert "Added" in text


def test_format_score_perfect():
    r = _make_result(unchanged={"x": {}})
    s = compute_score(r)
    text = format_score(s)
    assert "100.0%" in text
