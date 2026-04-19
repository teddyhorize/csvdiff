"""Tests for csvdiff.rename."""
import pytest
from csvdiff.rename import (
    RenameError,
    RenameOptions,
    build_rename_options,
    rename_headers,
    rename_rows,
    apply_renames,
)


def test_build_rename_options_basic():
    opts = build_rename_options(["old:new", "a:b"])
    assert opts.mapping == {"old": "new", "a": "b"}


def test_build_rename_options_empty():
    opts = build_rename_options([])
    assert opts.mapping == {}


def test_parse_invalid_pair_no_colon():
    with pytest.raises(RenameError, match="expected 'old:new'"):
        build_rename_options(["badpair"])


def test_parse_invalid_pair_empty_name():
    with pytest.raises(RenameError, match="must not be empty"):
        build_rename_options([":new"])


def test_rename_headers_applies_mapping():
    opts = RenameOptions(mapping={"id": "ID", "name": "Name"})
    result = rename_headers(["id", "name", "age"], opts)
    assert result == ["ID", "Name", "age"]


def test_rename_headers_no_mapping():
    opts = RenameOptions()
    result = rename_headers(["a", "b"], opts)
    assert result == ["a", "b"]


def test_rename_rows_renames_keys():
    opts = RenameOptions(mapping={"old_col": "new_col"})
    rows = [{"old_col": "1", "keep": "x"}]
    result = rename_rows(rows, opts)
    assert result == [{"new_col": "1", "keep": "x"}]


def test_rename_rows_empty_mapping():
    opts = RenameOptions()
    rows = [{"a": "1"}]
    assert rename_rows(rows, opts) is rows


def test_rename_rows_unknown_column_unchanged():
    opts = RenameOptions(mapping={"x": "y"})
    rows = [{"a": "1", "b": "2"}]
    result = rename_rows(rows, opts)
    assert result == [{"a": "1", "b": "2"}]


def test_apply_renames_both_sides():
    opts = RenameOptions(mapping={"col": "column"})
    a = [{"col": "1"}]
    b = [{"col": "2"}]
    ra, rb = apply_renames(a, b, opts)
    assert ra == [{"column": "1"}]
    assert rb == [{"column": "2"}]
