"""Tests for csvdiff.validate module."""
import pytest
from csvdiff.validate import (
    ValidationRule, validate_rows, format_validation, ValidateError
)


@pytest.fixture
def rows():
    return [
        {"name": "Alice", "age": "30", "code": "A001"},
        {"name": "", "age": "not_a_number", "code": "B999"},
        {"name": "Bob", "age": "25", "code": "XXXX"},
    ]


def test_validate_clean(rows):
    rules = [ValidationRule(column="name", not_empty=True)]
    result = validate_rows([rows[0], rows[2]], rules)
    assert result.is_clean()


def test_validate_not_empty_catches_blank(rows):
    rules = [ValidationRule(column="name", not_empty=True)]
    result = validate_rows(rows, rules)
    assert not result.is_clean()
    assert any(i.column == "name" and i.row_index == 1 for i in result.issues)


def test_validate_numeric_passes(rows):
    rules = [ValidationRule(column="age", numeric=True)]
    result = validate_rows([rows[0]], rules)
    assert result.is_clean()


def test_validate_numeric_fails(rows):
    rules = [ValidationRule(column="age", numeric=True)]
    result = validate_rows(rows, rules)
    issues = [i for i in result.issues if i.column == "age"]
    assert len(issues) == 1
    assert issues[0].reason == "not numeric"


def test_validate_pattern_matches(rows):
    rules = [ValidationRule(column="code", pattern=r"[A-B]\d{3}")]
    result = validate_rows([rows[0], rows[1]], rules)
    assert result.is_clean()


def test_validate_pattern_fails(rows):
    rules = [ValidationRule(column="code", pattern=r"[A-B]\d{3}")]
    result = validate_rows(rows, rules)
    issues = [i for i in result.issues if i.column == "code"]
    assert len(issues) == 1
    assert issues[0].row_index == 2


def test_validate_invalid_pattern(rows):
    rules = [ValidationRule(column="code", pattern=r"[")]
    with pytest.raises(ValidateError):
        validate_rows(rows, rules)


def test_format_validation_clean():
    from csvdiff.validate import ValidationResult
    result = ValidationResult()
    assert format_validation(result) == "No validation issues found."


def test_format_validation_with_issues(rows):
    rules = [ValidationRule(column="name", not_empty=True)]
    result = validate_rows(rows, rules)
    output = format_validation(result)
    assert "1 validation issue" in output
    assert "row 1" in output
    assert "name" in output


def test_multiple_rules_combined(rows):
    rules = [
        ValidationRule(column="name", not_empty=True),
        ValidationRule(column="age", numeric=True),
    ]
    result = validate_rows(rows, rules)
    assert len(result.issues) == 2
