import pytest
from csvdiff.differ import DiffResult
from csvdiff.stats import compute_stats, format_stats, DiffStats


@pytest.fixture
def empty_result():
    return DiffResult(
        added_rows=[],
        removed_rows=[],
        modified_rows=[],
        added_columns=[],
        removed_columns=[],
    )


@pytest.fixture
def full_result():
    return DiffResult(
        added_rows=[{"id": "3", "name": "Carol"}],
        removed_rows=[{"id": "2", "name": "Bob"}],
        modified_rows=[
            {"key": "1", "changes": {"name": ("Alice", "Alicia"), "age": ("30", "31")}}
        ],
        added_columns=["score"],
        removed_columns=["notes"],
    )


def test_compute_stats_empty(empty_result):
    stats = compute_stats(empty_result, 5, 5)
    assert stats.added_rows == 0
    assert stats.removed_rows == 0
    assert stats.modified_rows == 0
    assert stats.changed_fields == 0
    assert stats.change_rate == 0.0


def test_compute_stats_counts(full_result):
    stats = compute_stats(full_result, 10, 10)
    assert stats.added_rows == 1
    assert stats.removed_rows == 1
    assert stats.modified_rows == 1
    assert stats.added_columns == 1
    assert stats.removed_columns == 1


def test_compute_stats_changed_fields(full_result):
    stats = compute_stats(full_result, 10, 10)
    assert stats.changed_fields == 2
    assert stats.column_change_breakdown["name"] == 1
    assert stats.column_change_breakdown["age"] == 1


def test_compute_stats_change_rate(full_result):
    stats = compute_stats(full_result, 10, 10)
    # (1 added + 1 removed + 1 modified) / 10 * 100 = 30.0
    assert stats.change_rate == 30.0


def test_compute_stats_row_totals(full_result):
    stats = compute_stats(full_result, 8, 9)
    assert stats.total_rows_a == 8
    assert stats.total_rows_b == 9


def test_format_stats_contains_sections(full_result):
    stats = compute_stats(full_result, 10, 10)
    output = format_stats(stats)
    assert "Diff Statistics" in output
    assert "Added rows: 1" in output
    assert "Removed rows: 1" in output
    assert "Modified rows: 1" in output
    assert "Change rate:" in output
    assert "Changes by column:" in output
    assert "name: 1" in output


def test_format_stats_no_breakdown(empty_result):
    stats = compute_stats(empty_result, 5, 5)
    output = format_stats(stats)
    assert "Changes by column" not in output
