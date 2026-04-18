"""Tests for csvdiff.annotate."""
import pytest
from csvdiff.differ import DiffResult
from csvdiff.annotate import (
    annotate_diff, to_flat_dicts, format_annotation,
    ADDED_LABEL, REMOVED_LABEL, MODIFIED_LABEL, UNCHANGED_LABEL, ANNOTATION_KEY
)


@pytest.fixture
def result():
    return DiffResult(
        added_rows={"2": {"id": "2", "name": "Bob"}},
        removed_rows={"3": {"id": "3", "name": "Carol"}},
        modified_rows={"1": ({"id": "1", "name": "Alice"}, {"id": "1", "name": "Alicia"}, ["name"])},
        unchanged_rows={"4": {"id": "4", "name": "Dave"}},
        added_columns=[],
        removed_columns=[],
    )


def test_annotate_diff_counts(result):
    rows = annotate_diff(result)
    assert len(rows) == 3


def test_annotate_diff_labels(result):
    rows = annotate_diff(result)
    labels = {r.label for r in rows}
    assert ADDED_LABEL in labels
    assert REMOVED_LABEL in labels
    assert MODIFIED_LABEL in labels


def test_annotate_diff_include_unchanged(result):
    rows = annotate_diff(result, include_unchanged=True)
    labels = [r.label for r in rows]
    assert UNCHANGED_LABEL in labels
    assert len(rows) == 4


def test_annotate_modified_changed_fields(result):
    rows = annotate_diff(result)
    modified = [r for r in rows if r.label == MODIFIED_LABEL]
    assert len(modified) == 1
    assert "name" in modified[0].changed_fields


def test_to_flat_dicts_adds_annotation_key(result):
    rows = annotate_diff(result)
    flat = to_flat_dicts(rows)
    for d in flat:
        assert ANNOTATION_KEY in d


def test_to_flat_dicts_custom_key(result):
    rows = annotate_diff(result)
    flat = to_flat_dicts(rows, annotation_key="_status")
    for d in flat:
        assert "_status" in d


def test_to_flat_dicts_label_values(result):
    rows = annotate_diff(result)
    flat = to_flat_dicts(rows)
    label_values = {d[ANNOTATION_KEY] for d in flat}
    assert label_values == {ADDED_LABEL, REMOVED_LABEL, MODIFIED_LABEL}


def test_format_annotation_no_color(result):
    rows = annotate_diff(result)
    for ar in rows:
        s = format_annotation(ar, color=False)
        assert ar.label.upper() in s


def test_format_annotation_with_color(result):
    rows = annotate_diff(result)
    for ar in rows:
        s = format_annotation(ar, color=True)
        assert "\033[" in s
