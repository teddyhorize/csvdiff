"""Tests for csvdiff.lint."""

import pytest
from csvdiff.lint import (
    lint_rows, format_lint, LintResult,
    _check_empty_cells, _check_duplicate_keys, _check_type_consistency,
)


COLUMNS = ["id", "name", "score"]


@pytest.fixture
def clean_rows():
    return [
        {"id": "1", "name": "Alice", "score": "95"},
        {"id": "2", "name": "Bob", "score": "82"},
    ]


@pytest.fixture
def dirty_rows():
    return [
        {"id": "1", "name": "Alice", "score": "95"},
        {"id": "1", "name": "", "score": "bad"},
    ]


def test_lint_clean(clean_rows):
    result = lint_rows(clean_rows, COLUMNS)
    assert result.is_clean()


def test_lint_empty_rows():
    result = lint_rows([], COLUMNS)
    assert result.is_clean()


def test_empty_cell_detected():
    rows = [{"id": "1", "name": "", "score": "10"}]
    issues = _check_empty_cells(rows, COLUMNS)
    assert any(i.code == "EMPTY_CELL" and i.column == "name" for i in issues)


def test_no_empty_cells(clean_rows):
    issues = _check_empty_cells(clean_rows, COLUMNS)
    assert issues == []


def test_duplicate_key_detected():
    rows = [
        {"id": "1", "name": "Alice"},
        {"id": "1", "name": "Bob"},
    ]
    issues = _check_duplicate_keys(rows, "id")
    assert len(issues) == 1
    assert issues[0].code == "DUPLICATE_KEY"


def test_no_duplicate_keys(clean_rows):
    issues = _check_duplicate_keys(clean_rows, "id")
    assert issues == []


def test_type_mismatch_detected():
    rows = [
        {"score": "10"},
        {"score": "20"},
        {"score": "bad"},
    ]
    issues = _check_type_consistency(rows, ["score"])
    assert any(i.code == "TYPE_MISMATCH" for i in issues)


def test_type_consistent(clean_rows):
    issues = _check_type_consistency(clean_rows, ["score"])
    assert issues == []


def test_lint_rows_with_key(dirty_rows):
    result = lint_rows(dirty_rows, COLUMNS, key_column="id")
    codes = [i.code for i in result.issues]
    assert "DUPLICATE_KEY" in codes
    assert "EMPTY_CELL" in codes


def test_format_lint_clean():
    result = LintResult()
    assert "No lint" in format_lint(result)


def test_format_lint_issues(dirty_rows):
    result = lint_rows(dirty_rows, COLUMNS, key_column="id")
    text = format_lint(result)
    assert "lint issue" in text
    assert "DUPLICATE_KEY" in text or "EMPTY_CELL" in text
