"""Tests for csvdiff.pivot_table."""
import argparse

import pytest

from csvdiff.differ import DiffResult
from csvdiff.pivot_table import (
    PivotCell,
    PivotTableError,
    build_pivot_table,
    format_pivot_table,
)
from csvdiff.cli_pivot_table import (
    pivot_table_as_dict,
    register_pivot_table_args,
    maybe_print_pivot_table,
)


@pytest.fixture()
def base_result() -> DiffResult:
    return DiffResult(
        added_rows=[
            {"region": "North", "product": "Widget", "qty": "10"},
            {"region": "South", "product": "Gadget", "qty": "5"},
        ],
        removed_rows=[
            {"region": "North", "product": "Gadget", "qty": "3"},
        ],
        modified_rows=[
            {
                "old": {"region": "South", "product": "Widget", "qty": "7"},
                "new": {"region": "South", "product": "Widget", "qty": "9"},
            }
        ],
        added_columns=[],
        removed_columns=[],
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(
        added_rows=[],
        removed_rows=[],
        modified_rows=[],
        added_columns=[],
        removed_columns=[],
    )


def test_build_pivot_table_row_keys(base_result):
    table = build_pivot_table(base_result, "region", "product")
    assert set(table.row_keys) == {"North", "South"}


def test_build_pivot_table_col_keys(base_result):
    table = build_pivot_table(base_result, "region", "product")
    assert set(table.col_keys) == {"Widget", "Gadget"}


def test_build_pivot_table_added_count(base_result):
    table = build_pivot_table(base_result, "region", "product")
    assert table.cells["North"]["Widget"].added == 1


def test_build_pivot_table_removed_count(base_result):
    table = build_pivot_table(base_result, "region", "product")
    assert table.cells["North"]["Gadget"].removed == 1


def test_build_pivot_table_modified_count(base_result):
    table = build_pivot_table(base_result, "region", "product")
    assert table.cells["South"]["Widget"].modified == 1


def test_build_pivot_table_empty_result(empty_result):
    table = build_pivot_table(empty_result, "region", "product")
    assert table.row_keys == []
    assert table.col_keys == []


def test_build_pivot_table_missing_row_field(base_result):
    with pytest.raises(PivotTableError, match="Row field"):
        build_pivot_table(base_result, "nonexistent", "product")


def test_build_pivot_table_missing_col_field(base_result):
    with pytest.raises(PivotTableError, match="Column field"):
        build_pivot_table(base_result, "region", "nonexistent")


def test_format_pivot_table_empty(empty_result):
    table = build_pivot_table(empty_result, "region", "product")
    text = format_pivot_table(table)
    assert "no changes" in text


def test_format_pivot_table_contains_row_key(base_result):
    table = build_pivot_table(base_result, "region", "product")
    text = format_pivot_table(table)
    assert "North" in text
    assert "South" in text


def test_pivot_table_as_dict_keys(base_result):
    table = build_pivot_table(base_result, "region", "product")
    d = pivot_table_as_dict(table)
    assert "row_field" in d
    assert "col_field" in d
    assert "cells" in d
    assert d["row_field"] == "region"


def test_register_pivot_table_args():
    parser = argparse.ArgumentParser()
    register_pivot_table_args(parser)
    args = parser.parse_args(["--pivot-row", "region", "--pivot-col", "product"])
    assert args.pivot_row == "region"
    assert args.pivot_col == "product"


def test_maybe_print_pivot_table_no_args(base_result, capsys):
    parser = argparse.ArgumentParser()
    register_pivot_table_args(parser)
    args = parser.parse_args([])
    result = maybe_print_pivot_table(args, base_result)
    assert result is None
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_print_pivot_table_with_args(base_result, capsys):
    parser = argparse.ArgumentParser()
    register_pivot_table_args(parser)
    args = parser.parse_args(["--pivot-row", "region", "--pivot-col", "product"])
    result = maybe_print_pivot_table(args, base_result)
    assert result is not None
    captured = capsys.readouterr()
    assert "region" in captured.out
