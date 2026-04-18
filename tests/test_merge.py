import pytest
from csvdiff.merge import MergeOptions, MergeResult, merge_rows, MergeError


LEFT = [
    {"id": "1", "name": "Alice", "score": "10"},
    {"id": "2", "name": "Bob",   "score": "20"},
]

RIGHT = [
    {"id": "1", "name": "Alice", "score": "99"},
    {"id": "3", "name": "Carol", "score": "30"},
]


def opts(**kw):
    return MergeOptions(key_column="id", **kw)


def test_merge_keeps_left_only_rows():
    result = merge_rows(LEFT, RIGHT, opts())
    keys = [r["id"] for r in result.rows]
    assert "2" in keys


def test_merge_adds_right_only_rows():
    result = merge_rows(LEFT, RIGHT, opts())
    keys = [r["id"] for r in result.rows]
    assert "3" in keys
    assert result.added_from_right == 1


def test_merge_prefers_right_on_conflict():
    result = merge_rows(LEFT, RIGHT, opts(prefer="right"))
    row = next(r for r in result.rows if r["id"] == "1")
    assert row["score"] == "99"
    assert result.conflicts_resolved == 1


def test_merge_prefers_left_on_conflict():
    result = merge_rows(LEFT, RIGHT, opts(prefer="left"))
    row = next(r for r in result.rows if r["id"] == "1")
    assert row["score"] == "10"
    assert result.conflicts_resolved == 1


def test_merge_no_conflict_no_count():
    right_no_conflict = [{"id": "1", "name": "Alice", "score": "10"}]
    result = merge_rows(LEFT[:1], right_no_conflict, opts())
    assert result.conflicts_resolved == 0


def test_merge_fill_missing_adds_empty_cells():
    left = [{"id": "1", "name": "Alice"}]
    right = [{"id": "2", "name": "Bob", "score": "5"}]
    result = merge_rows(left, right, opts(fill_missing=True))
    for row in result.rows:
        assert "score" in row


def test_merge_missing_key_raises():
    bad = [{"name": "X"}]
    with pytest.raises(MergeError):
        merge_rows(bad, RIGHT, opts())


def test_merge_empty_left():
    result = merge_rows([], RIGHT, opts())
    assert len(result.rows) == len(RIGHT)


def test_merge_empty_right():
    result = merge_rows(LEFT, [], opts())
    assert len(result.rows) == len(LEFT)
    assert result.added_from_right == 0


def test_merge_result_columns_union():
    left = [{"id": "1", "a": "x"}]
    right = [{"id": "1", "b": "y"}]
    result = merge_rows(left, right, opts())
    assert "a" in result.columns
    assert "b" in result.columns
