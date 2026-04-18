"""Tests for csvdiff.summary module."""
import pytest
from csvdiff.differ import DiffResult
from csvdiff.summary import summarize, format_summary, DiffSummary


@pytest.fixture
def empty_result():
    return DiffResult(
        added_rows=[],
        removed_rows=[],
        modified_rows=[],
        added_columns=set(),
        removed_columns=set(),
    )


@pytest.fixture
def full_result():
    return DiffResult(
        added_rows=[{"id": "3", "name": "Carol"}],
        removed_rows=[{"id": "2", "name": "Bob"}],
        modified_rows=[{"key": "1", "field": "name", "old": "Alice", "new": "Alicia"}],
        added_columns={"email"},
        removed_columns={"phone"},
    )


def test_summarize_clean(empty_result):
    summary = summarize(empty_result)
    assert summary.is_clean()
    assert summary.total_changes == 0


def test_summarize_counts(full_result):
    summary = summarize(full_result)
    assert summary.added_rows == 1
    assert summary.removed_rows == 1
    assert summary.modified_rows == 1
    assert "email" in summary.added_columns
    assert "phone" in summary.removed_columns
    assert summary.total_changes == 5


def test_summarize_not_clean(full_result):
    summary = summarize(full_result)
    assert not summary.is_clean()


def test_format_summary_clean(empty_result):
    summary = summarize(empty_result)
    assert format_summary(summary) == "No differences found."


def test_format_summary_contains_counts(full_result):
    summary = summarize(full_result)
    text = format_summary(summary)
    assert "Rows added:" in text
    assert "Rows removed:" in text
    assert "Rows modified:" in text
    assert "email" in text
    assert "phone" in text
    assert "Total changes: 5" in text


def test_as_dict(full_result):
    summary = summarize(full_result)
    d = summary.as_dict()
    assert d["added_rows"] == 1
    assert d["total_changes"] == 5
    assert isinstance(d["added_columns"], list)


def test_as_dict_columns_are_sorted(full_result):
    """Columns in as_dict output should be sorted for deterministic output."""
    result = DiffResult(
        added_rows=[],
        removed_rows=[],
        modified_rows=[],
        added_columns={"zebra", "apple", "mango"},
        removed_columns={"omega", "alpha"},
    )
    summary = summarize(result)
    d = summary.as_dict()
    assert d["added_columns"] == sorted(d["added_columns"])
    assert d["removed_columns"] == sorted(d["removed_columns"])
