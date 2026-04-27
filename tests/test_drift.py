"""Tests for csvdiff.drift."""
import pytest

from csvdiff.differ import DiffResult
from csvdiff.drift import DriftReport, detect_drift, format_drift
from csvdiff.schema import compare_schemas


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(
    added=None, removed=None, modified=None, added_columns=None, removed_columns=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
        added_columns=added_columns or [],
        removed_columns=removed_columns or [],
    )


OLD_HEADERS = ["id", "name", "score"]
NEW_HEADERS = ["id", "name", "score"]


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_detect_drift_no_changes():
    result = _make_result()
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result)
    assert not report.has_drift


def test_detect_drift_added_rows():
    result = _make_result(added=[{"id": "3", "name": "Carol", "score": "90"}])
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result)
    assert report.has_drift
    assert report.added_rows == 1
    assert report.removed_rows == 0


def test_detect_drift_removed_rows():
    result = _make_result(removed=[{"id": "1", "name": "Alice", "score": "80"}])
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result)
    assert report.removed_rows == 1


def test_detect_drift_modified_rows_counts_columns():
    modified = [
        {"old": {"id": "1", "score": "80"}, "new": {"id": "1", "score": "95"}},
        {"old": {"id": "2", "score": "70"}, "new": {"id": "2", "score": "75"}},
    ]
    result = _make_result(modified=modified)
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result)
    assert report.modified_rows == 2
    assert report.changed_columns.get("score") == 2


def test_detect_drift_schema_added_column():
    result = _make_result()
    report = detect_drift(OLD_HEADERS, OLD_HEADERS + ["grade"], result)
    assert report.has_drift
    assert "grade" in report.schema_drift.added_columns


def test_detect_drift_schema_removed_column():
    result = _make_result()
    report = detect_drift(OLD_HEADERS, ["id", "name"], result)
    assert "score" in report.schema_drift.removed_columns


def test_detect_drift_label_stored():
    result = _make_result()
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result, label="weekly")
    assert report.label == "weekly"


# ---------------------------------------------------------------------------
# format_drift
# ---------------------------------------------------------------------------

def test_format_drift_clean():
    result = _make_result()
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result)
    text = format_drift(report)
    assert "No drift detected" in text


def test_format_drift_shows_added_rows():
    result = _make_result(added=[{"id": "5"}])
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result)
    text = format_drift(report)
    assert "Added rows" in text
    assert "1" in text


def test_format_drift_includes_label():
    result = _make_result(added=[{"id": "5"}])
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result, label="run-42")
    text = format_drift(report)
    assert "run-42" in text


def test_format_drift_shows_hot_columns():
    modified = [
        {"old": {"score": "1"}, "new": {"score": "2"}},
        {"old": {"score": "3"}, "new": {"score": "4"}},
    ]
    result = _make_result(modified=modified)
    report = detect_drift(OLD_HEADERS, NEW_HEADERS, result)
    text = format_drift(report)
    assert "score" in text
