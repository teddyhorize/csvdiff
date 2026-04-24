"""Tests for csvdiff.timeline."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult
from csvdiff.timeline import (
    Timeline,
    TimelineEntry,
    TimelineError,
    add_entry,
    format_timeline,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _result(
    added=None, removed=None, modified=None,
    added_columns=None, removed_columns=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
        added_columns=added_columns or [],
        removed_columns=removed_columns or [],
    )


# ---------------------------------------------------------------------------
# TimelineEntry
# ---------------------------------------------------------------------------

def test_entry_total_changes():
    e = TimelineEntry(
        timestamp="2024-01-01T00:00:00Z",
        label="run1",
        added=2, removed=1, modified=3,
    )
    assert e.total_changes == 6


def test_entry_is_clean_true():
    e = TimelineEntry(timestamp="t", label="l", added=0, removed=0, modified=0)
    assert e.is_clean is True


def test_entry_is_clean_false_when_added():
    e = TimelineEntry(timestamp="t", label="l", added=1, removed=0, modified=0)
    assert e.is_clean is False


def test_entry_is_clean_false_when_added_columns():
    e = TimelineEntry(
        timestamp="t", label="l", added=0, removed=0, modified=0,
        added_columns=["x"]
    )
    assert e.is_clean is False


# ---------------------------------------------------------------------------
# add_entry
# ---------------------------------------------------------------------------

def test_add_entry_appends_to_timeline():
    tl = Timeline()
    result = _result(added=[{"id": "1"}])
    add_entry(tl, result, label="v1", timestamp="2024-01-01T00:00:00Z")
    assert len(tl) == 1


def test_add_entry_counts_match_result():
    tl = Timeline()
    result = _result(added=[{"a": "1"}, {"a": "2"}], removed=[{"a": "3"}])
    entry = add_entry(tl, result, label="v2", timestamp="2024-01-02T00:00:00Z")
    assert entry.added == 2
    assert entry.removed == 1
    assert entry.modified == 0


def test_add_entry_empty_label_raises():
    tl = Timeline()
    with pytest.raises(TimelineError):
        add_entry(tl, _result(), label="")


def test_add_entry_uses_provided_timestamp():
    tl = Timeline()
    entry = add_entry(tl, _result(), label="x", timestamp="2000-06-15T12:00:00Z")
    assert entry.timestamp == "2000-06-15T12:00:00Z"


def test_add_entry_auto_timestamp_when_none():
    tl = Timeline()
    entry = add_entry(tl, _result(), label="auto")
    assert "T" in entry.timestamp  # ISO-like


# ---------------------------------------------------------------------------
# format_timeline
# ---------------------------------------------------------------------------

def test_format_timeline_empty():
    assert "no timeline" in format_timeline(Timeline())


def test_format_timeline_contains_label():
    tl = Timeline()
    add_entry(tl, _result(), label="release-1.0", timestamp="2024-01-01T00:00:00Z")
    output = format_timeline(tl)
    assert "release-1.0" in output


def test_format_timeline_multiple_entries():
    tl = Timeline()
    add_entry(tl, _result(added=[{"a": "1"}]), label="a", timestamp="2024-01-01T00:00:00Z")
    add_entry(tl, _result(removed=[{"a": "2"}]), label="b", timestamp="2024-01-02T00:00:00Z")
    output = format_timeline(tl)
    assert "a" in output
    assert "b" in output
