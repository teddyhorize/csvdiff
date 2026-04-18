import pytest
from csvdiff.pivot import pivot_by_column, format_pivot, ColumnPivot


@pytest.fixture
def empty_result():
    return {"added": [], "removed": [], "modified": []}


@pytest.fixture
def full_result():
    return {
        "added": [{"id": "3", "name": "Carol", "age": "28"}],
        "removed": [{"id": "2", "name": "Bob", "age": "30"}],
        "modified": [
            {"old": {"id": "1", "name": "Alice", "age": "25"},
             "new": {"id": "1", "name": "Alice", "age": "26"}}
        ],
    }


def test_pivot_empty(empty_result):
    pivots = pivot_by_column(empty_result)
    assert pivots == {}


def test_pivot_added_rows(full_result):
    pivots = pivot_by_column(full_result)
    assert "name" in pivots
    assert "Carol" in pivots["name"].added_values


def test_pivot_removed_rows(full_result):
    pivots = pivot_by_column(full_result)
    assert "Bob" in pivots["name"].removed_values


def test_pivot_modified_rows(full_result):
    pivots = pivot_by_column(full_result)
    assert "age" in pivots
    assert ("25", "26") in pivots["age"].modified_values


def test_pivot_unmodified_column_not_in_modified(full_result):
    pivots = pivot_by_column(full_result)
    # 'name' was not changed in the modified entry
    name_pivot = pivots.get("name")
    assert name_pivot is None or len(name_pivot.modified_values) == 0


def test_total_changes(full_result):
    pivots = pivot_by_column(full_result)
    assert pivots["age"].total_changes >= 1


def test_format_pivot_empty(empty_result):
    pivots = pivot_by_column(empty_result)
    out = format_pivot(pivots)
    assert "No column-level" in out


def test_format_pivot_contains_column(full_result):
    pivots = pivot_by_column(full_result)
    out = format_pivot(pivots, color=False)
    assert "age" in out
    assert "name" in out


def test_format_pivot_no_color(full_result):
    pivots = pivot_by_column(full_result)
    out = format_pivot(pivots, color=False)
    assert "\033[" not in out


def test_format_pivot_with_color(full_result):
    pivots = pivot_by_column(full_result)
    out = format_pivot(pivots, color=True)
    assert "\033[" in out
