"""Tests for csvdiff.schema module."""

from csvdiff.schema import compare_schemas, format_schema_diff, SchemaDiff


def test_identical_schemas():
    diff = compare_schemas(["id", "name"], ["id", "name"])
    assert not diff.has_changes
    assert diff.added_columns == []
    assert diff.removed_columns == []
    assert not diff.reordered


def test_added_column():
    diff = compare_schemas(["id", "name"], ["id", "name", "email"])
    assert diff.added_columns == ["email"]
    assert diff.removed_columns == []
    assert diff.has_changes


def test_removed_column():
    diff = compare_schemas(["id", "name", "age"], ["id", "name"])
    assert diff.removed_columns == ["age"]
    assert diff.added_columns == []
    assert diff.has_changes


def test_reordered_columns():
    diff = compare_schemas(["id", "name", "age"], ["id", "age", "name"])
    assert diff.reordered
    assert not diff.added_columns
    assert not diff.removed_columns


def test_added_and_removed():
    diff = compare_schemas(["id", "name"], ["id", "email"])
    assert diff.added_columns == ["email"]
    assert diff.removed_columns == ["name"]


def test_format_no_changes():
    diff = compare_schemas(["id"], ["id"])
    assert format_schema_diff(diff) == "Schemas are identical."


def test_format_with_changes():
    diff = compare_schemas(["id", "name"], ["id", "email"])
    text = format_schema_diff(diff)
    assert "Added" in text
    assert "Removed" in text
    assert "email" in text
    assert "name" in text


def test_format_reorder():
    diff = compare_schemas(["a", "b", "c"], ["a", "c", "b"])
    text = format_schema_diff(diff)
    assert "order" in text.lower()
