"""Tests for csvdiff.highlight."""
import pytest
from csvdiff.highlight import (
    CellDiff,
    RowHighlight,
    highlight_row,
    highlight_modified,
    format_highlight,
)


OLD = {"id": "1", "name": "Alice", "age": "30"}
NEW = {"id": "1", "name": "Alicia", "age": "31"}


def test_highlight_row_detects_changes():
    rh = highlight_row(OLD, NEW, key="1")
    assert rh.key == "1"
    assert len(rh.diffs) == 2


def test_highlight_row_changed_columns():
    rh = highlight_row(OLD, NEW, key="1")
    assert set(rh.changed_columns()) == {"name", "age"}


def test_highlight_row_no_changes():
    rh = highlight_row(OLD, OLD, key="1")
    assert rh.diffs == []


def test_highlight_row_missing_column_in_new():
    rh = highlight_row({"id": "1", "extra": "val"}, {"id": "1"}, key="1")
    assert any(d.column == "extra" for d in rh.diffs)


def test_highlight_row_missing_column_in_old():
    rh = highlight_row({"id": "1"}, {"id": "1", "extra": "val"}, key="1")
    assert any(d.column == "extra" for d in rh.diffs)
    diff = next(d for d in rh.diffs if d.column == "extra")
    assert diff.old_value == ""
    assert diff.new_value == "val"


def test_highlight_modified_multiple_rows():
    modified = {
        "1": (OLD, NEW),
        "2": ({"id": "2", "name": "Bob"}, {"id": "2", "name": "Bob"}),
    }
    highlights = highlight_modified(modified)
    assert len(highlights) == 1
    assert highlights[0].key == "1"


def test_highlight_modified_empty():
    assert highlight_modified({}) == []


def test_format_highlight_no_changes():
    result = format_highlight([])
    assert "No cell-level" in result


def test_format_highlight_with_color():
    rh = highlight_row(OLD, NEW, key="1")
    output = format_highlight([rh], use_color=True)
    assert "\033[31m" in output
    assert "\033[32m" in output


def test_format_highlight_no_color():
    rh = highlight_row(OLD, NEW, key="1")
    output = format_highlight([rh], use_color=False)
    assert "\033[" not in output
    assert "Alice" in output
    assert "Alicia" in output


def test_format_highlight_empty_value_shown():
    rh = highlight_row({"id": "1", "note": ""}, {"id": "1", "note": "hi"}, key="1")
    output = format_highlight([rh], use_color=False)
    assert "(empty)" in output
