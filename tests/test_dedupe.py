import pytest
from csvdiff.dedupe import find_duplicates, format_dedupe, DedupeError, DedupeResult


ROWS = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "1", "name": "Alice"},
    {"id": "3", "name": "Carol"},
    {"id": "2", "name": "Bob"},
    {"id": "2", "name": "Bob"},
]


def test_no_duplicates():
    rows = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    result = find_duplicates(rows)
    assert result.total_duplicates == 0
    assert result.duplicate_groups == {}


def test_finds_duplicates():
    result = find_duplicates(ROWS)
    assert result.total_duplicates == 3  # 1 extra Alice, 2 extra Bobs


def test_duplicate_groups_keys():
    result = find_duplicates(ROWS)
    assert len(result.duplicate_groups) == 2


def test_checked_columns_default():
    rows = [{"id": "1", "name": "Alice"}, {"id": "1", "name": "Alice"}]
    result = find_duplicates(rows)
    assert result.checked_columns == ["id", "name"]


def test_checked_columns_subset():
    result = find_duplicates(ROWS, columns=["id"])
    assert result.checked_columns == ["id"]


def test_subset_column_dedup():
    rows = [
        {"id": "1", "name": "Alice"},
        {"id": "1", "name": "AliceB"},
    ]
    result = find_duplicates(rows, columns=["id"])
    assert result.total_duplicates == 1


def test_invalid_column_raises():
    rows = [{"id": "1"}]
    with pytest.raises(DedupeError):
        find_duplicates(rows, columns=["nonexistent"])


def test_empty_rows():
    result = find_duplicates([])
    assert result.total_duplicates == 0


def test_format_no_duplicates():
    result = DedupeResult()
    assert "No duplicate" in format_dedupe(result)


def test_format_with_duplicates():
    result = find_duplicates(ROWS)
    output = format_dedupe(result)
    assert "duplicate" in output.lower()
    assert "occurrences" in output


def test_format_color():
    result = find_duplicates(ROWS)
    output = format_dedupe(result, color=True)
    assert "\033[33m" in output
