import pytest
from csvdiff.sort import SortOptions, SortError, sort_rows, sort_pair


@pytest.fixture
def rows():
    return [
        {"name": "Charlie", "age": "30"},
        {"name": "alice", "age": "25"},
        {"name": "Bob", "age": "20"},
    ]


def test_sort_rows_no_options(rows):
    result = sort_rows(rows)
    assert result == rows


def test_sort_rows_empty_columns(rows):
    opts = SortOptions(columns=[])
    result = sort_rows(rows, opts)
    assert result == rows


def test_sort_rows_by_column(rows):
    opts = SortOptions(columns=["age"])
    result = sort_rows(rows, opts)
    assert [r["age"] for r in result] == ["20", "25", "30"]


def test_sort_rows_reverse(rows):
    opts = SortOptions(columns=["age"], reverse=True)
    result = sort_rows(rows, opts)
    assert result[0]["age"] == "30"


def test_sort_rows_case_sensitive(rows):
    opts = SortOptions(columns=["name"], case_sensitive=True)
    result = sort_rows(rows, opts)
    # uppercase letters sort before lowercase in ASCII
    assert result[0]["name"] == "Bob"


def test_sort_rows_case_insensitive(rows):
    opts = SortOptions(columns=["name"], case_sensitive=False)
    result = sort_rows(rows, opts)
    assert result[0]["name"] == "alice"


def test_sort_rows_missing_column(rows):
    opts = SortOptions(columns=["nonexistent"])
    with pytest.raises(SortError, match="nonexistent"):
        sort_rows(rows, opts)


def test_sort_rows_empty_list():
    opts = SortOptions(columns=["name"])
    result = sort_rows([], opts)
    assert result == []


def test_sort_pair():
    a = [{"id": "2"}, {"id": "1"}]
    b = [{"id": "3"}, {"id": "1"}]
    opts = SortOptions(columns=["id"])
    sa, sb = sort_pair(a, b, opts)
    assert sa[0]["id"] == "1"
    assert sb[0]["id"] == "1"


def test_sort_pair_no_options():
    a = [{"id": "2"}]
    b = [{"id": "1"}]
    sa, sb = sort_pair(a, b)
    assert sa == a and sb == b
