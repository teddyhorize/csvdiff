"""Tests for the diff result formatter."""

import pytest
from csvdiff.differ import DiffResult
from csvdiff.formatter import format_diff, FormatOptions


@pytest.fixture
def empty_result():
    return DiffResult()


@pytest.fixture
def full_result():
    return DiffResult(
        added_rows={"3": {"id": "3", "name": "Charlie"}},
        removed_rows={"2": {"id": "2", "name": "Bob"}},
        modified_rows={"1": {"name": ("Alice", "Alicia")}},
        added_columns=["email"],
        removed_columns=[],
    )


def test_no_diff_message(empty_result):
    output = format_diff(empty_result, FormatOptions(color=False))
    assert "No differences found" in output


def test_added_rows_shown(full_result):
    output = format_diff(full_result, FormatOptions(color=False))
    assert "Added rows" in output
    assert "Charlie" in output


def test_removed_rows_shown(full_result):
    output = format_diff(full_result, FormatOptions(color=False))
    assert "Removed rows" in output
    assert "Bob" in output


def test_modified_rows_shown(full_result):
    output = format_diff(full_result, FormatOptions(color=False))
    assert "Modified rows" in output
    assert "Alice" in output
    assert "Alicia" in output


def test_added_columns_shown(full_result):
    output = format_diff(full_result, FormatOptions(color=False))
    assert "email" in output


def test_summary_shown(full_result):
    output = format_diff(full_result, FormatOptions(color=False, show_summary=True))
    assert "Summary" in output
    assert "1 added" in output
    assert "1 removed" in output
    assert "1 modified" in output


def test_compact_hides_details(full_result):
    output = format_diff(full_result, FormatOptions(color=False, compact=True))
    assert "Added rows" in output
    assert "Charlie" not in output


def test_color_codes_present(full_result):
    output = format_diff(full_result, FormatOptions(color=True))
    assert "\033[" in output


def test_no_color_codes_when_disabled(full_result):
    output = format_diff(full_result, FormatOptions(color=False))
    assert "\033[" not in output
