"""Tests for csvdiff.heatmap."""
import pytest

from csvdiff.differ import DiffResult
from csvdiff.heatmap import (
    HeatmapCell,
    build_heatmap,
    format_heatmap,
    _count_column_changes,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified={}, added_columns=[], removed_columns=[])


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Carol", "score": "90"}],
        removed=[{"id": "4", "name": "Dave", "score": "55"}],
        modified={
            "1": {"score": ("80", "85"), "name": ("Alice", "Alicia")},
            "2": {"score": ("70", "72")},
        },
        added_columns=[],
        removed_columns=[],
    )


# ---------------------------------------------------------------------------
# _count_column_changes
# ---------------------------------------------------------------------------

def test_count_column_changes_empty(empty_result):
    assert _count_column_changes(empty_result) == {}


def test_count_column_changes_basic(diff_result):
    counts = _count_column_changes(diff_result)
    assert counts["score"] == 2
    assert counts["name"] == 1


# ---------------------------------------------------------------------------
# build_heatmap
# ---------------------------------------------------------------------------

def test_build_heatmap_empty(empty_result):
    hm = build_heatmap(empty_result)
    assert hm.columns == []
    assert hm.cells == {}
    assert hm.max_changes == 0


def test_build_heatmap_columns(diff_result):
    hm = build_heatmap(diff_result)
    assert "score" in hm.columns
    assert "name" in hm.columns


def test_build_heatmap_max_changes(diff_result):
    hm = build_heatmap(diff_result)
    assert hm.max_changes == 2


def test_build_heatmap_intensity_highest(diff_result):
    hm = build_heatmap(diff_result)
    assert hm.cells["score"].intensity == pytest.approx(1.0)


def test_build_heatmap_intensity_lower(diff_result):
    hm = build_heatmap(diff_result)
    assert hm.cells["name"].intensity == pytest.approx(0.5)


def test_build_heatmap_explicit_columns(diff_result):
    hm = build_heatmap(diff_result, columns=["score"])
    assert hm.columns == ["score"]
    assert "name" not in hm.cells


def test_build_heatmap_explicit_missing_column(diff_result):
    hm = build_heatmap(diff_result, columns=["score", "unknown"])
    assert hm.cells["unknown"].change_count == 0
    assert hm.cells["unknown"].intensity == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# format_heatmap
# ---------------------------------------------------------------------------

def test_format_heatmap_empty(empty_result):
    hm = build_heatmap(empty_result)
    output = format_heatmap(hm, use_color=False)
    assert "no column changes" in output


def test_format_heatmap_contains_column_name(diff_result):
    hm = build_heatmap(diff_result)
    output = format_heatmap(hm, use_color=False)
    assert "score" in output
    assert "name" in output


def test_format_heatmap_contains_change_count(diff_result):
    hm = build_heatmap(diff_result)
    output = format_heatmap(hm, use_color=False)
    assert "2" in output


def test_format_heatmap_no_ansi_when_disabled(diff_result):
    hm = build_heatmap(diff_result)
    output = format_heatmap(hm, use_color=False)
    assert "\033[" not in output


def test_format_heatmap_has_ansi_when_enabled(diff_result):
    hm = build_heatmap(diff_result)
    output = format_heatmap(hm, use_color=True)
    assert "\033[" in output
