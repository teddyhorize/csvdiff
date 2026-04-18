import pytest
from csvdiff.ignore import (
    IgnoreOptions,
    IgnoreError,
    apply_column_ignores,
    apply_row_ignores,
    apply_ignores,
)

SAMPLE = [
    {"id": "1", "name": "Alice", "secret": "x"},
    {"id": "2", "name": "Bob", "secret": "y"},
    {"id": "3", "name": "IGNORE_ME", "secret": "z"},
]


def test_apply_column_ignores_removes_column():
    result = apply_column_ignores(SAMPLE, ["secret"])
    assert all("secret" not in row for row in result)
    assert all("id" in row for row in result)


def test_apply_column_ignores_empty_list():
    result = apply_column_ignores(SAMPLE, [])
    assert result == SAMPLE


def test_apply_column_ignores_multiple():
    result = apply_column_ignores(SAMPLE, ["secret", "name"])
    assert all(set(row.keys()) == {"id"} for row in result)


def test_apply_row_ignores_filters_match():
    result = apply_row_ignores(SAMPLE, "IGNORE_ME")
    assert len(result) == 2
    assert all(row["name"] != "IGNORE_ME" for row in result)


def test_apply_row_ignores_no_pattern():
    result = apply_row_ignores(SAMPLE, None)
    assert result == SAMPLE


def test_apply_row_ignores_invalid_pattern():
    with pytest.raises(IgnoreError):
        apply_row_ignores(SAMPLE, "[invalid")


def test_apply_row_ignores_regex():
    result = apply_row_ignores(SAMPLE, r"^1,")
    assert len(result) == 2
    assert result[0]["id"] == "2"


def test_apply_ignores_combined():
    opts = IgnoreOptions(columns=["secret"], row_pattern="IGNORE_ME")
    result = apply_ignores(SAMPLE, opts)
    assert len(result) == 2
    assert all("secret" not in row for row in result)


def test_apply_ignores_empty_options():
    opts = IgnoreOptions()
    result = apply_ignores(SAMPLE, opts)
    assert result == SAMPLE
