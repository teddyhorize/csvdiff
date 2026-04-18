import pytest
from csvdiff.differ import DiffResult
from csvdiff.group import (
    GroupError,
    GroupStats,
    group_diff,
    all_groups,
    format_group_stats,
)


@pytest.fixture
def result():
    return DiffResult(
        added_rows=[{"region": "east", "val": "1"}, {"region": "west", "val": "2"}],
        removed_rows=[{"region": "east", "val": "0"}],
        modified_rows=[
            ({"region": "west", "val": "3"}, {"region": "west", "val": "4"}),
            ({"region": "east", "val": "5"}, {"region": "east", "val": "6"}),
        ],
        added_columns=[],
        removed_columns=[],
    )


def test_group_diff_added(result):
    stats = group_diff(result, "region")
    assert stats.added["east"] == 1
    assert stats.added["west"] == 1


def test_group_diff_removed(result):
    stats = group_diff(result, "region")
    assert stats.removed["east"] == 1
    assert "west" not in stats.removed


def test_group_diff_modified(result):
    stats = group_diff(result, "region")
    assert stats.modified["west"] == 1
    assert stats.modified["east"] == 1


def test_group_diff_empty_column_raises():
    r = DiffResult([], [], [], [], [])
    with pytest.raises(GroupError):
        group_diff(r, "")


def test_group_diff_missing_column_uses_missing_key(result):
    stats = group_diff(result, "nonexistent")
    assert stats.added.get("__missing__", 0) == 2


def test_all_groups(result):
    stats = group_diff(result, "region")
    groups = all_groups(stats)
    assert "east" in groups
    assert "west" in groups


def test_all_groups_empty():
    r = DiffResult([], [], [], [], [])
    stats = group_diff(r, "region")
    assert all_groups(stats) == []


def test_format_group_stats_no_diff():
    r = DiffResult([], [], [], [], [])
    stats = group_diff(r, "region")
    out = format_group_stats(stats)
    assert "no differences" in out


def test_format_group_stats_with_diff(result):
    stats = group_diff(result, "region")
    out = format_group_stats(stats)
    assert "east" in out
    assert "west" in out
    assert "+1" in out
