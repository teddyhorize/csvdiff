"""Tests for csvdiff.density and csvdiff.cli_density."""
from __future__ import annotations

import argparse
import json
from typing import Dict, List

import pytest

from csvdiff.density import (
    ColumnDensity,
    DensityError,
    DensityResult,
    compute_density,
    format_density,
)
from csvdiff.cli_density import density_as_dict, maybe_print_density, register_density_args


@pytest.fixture()
def rows() -> List[Dict[str, str]]:
    return [
        {"name": "Alice", "age": "30", "city": "NYC"},
        {"name": "Bob", "age": "", "city": "LA"},
        {"name": "", "age": "25", "city": ""},
    ]


def test_compute_density_empty():
    result = compute_density([])
    assert result.total_rows == 0
    assert result.columns == []


def test_compute_density_total_rows(rows):
    result = compute_density(rows)
    assert result.total_rows == 3


def test_compute_density_column_names(rows):
    result = compute_density(rows)
    names = [c.column for c in result.columns]
    assert names == ["name", "age", "city"]


def test_compute_density_full_column(rows):
    result = compute_density(rows)
    city = result.by_column("city")
    assert city.non_empty_cells == 2
    assert city.total_cells == 3
    assert pytest.approx(city.density, rel=1e-3) == 2 / 3


def test_compute_density_partial_column(rows):
    result = compute_density(rows)
    age = result.by_column("age")
    assert age.non_empty_cells == 2
    assert age.empty_cells == 1


def test_by_column_raises_on_missing(rows):
    result = compute_density(rows)
    with pytest.raises(DensityError, match="not found"):
        result.by_column("nonexistent")


def test_format_density_no_data():
    result = DensityResult(columns=[], total_rows=0)
    assert format_density(result) == "No data."


def test_format_density_contains_column_name(rows):
    result = compute_density(rows)
    text = format_density(result)
    assert "name" in text
    assert "age" in text


def test_format_density_shows_percentage(rows):
    result = compute_density(rows)
    text = format_density(result)
    assert "%" in text


def test_density_as_dict_keys(rows):
    result = compute_density(rows)
    d = density_as_dict(result)
    assert "total_rows" in d
    assert "columns" in d
    assert d["total_rows"] == 3


def test_density_as_dict_column_entry(rows):
    result = compute_density(rows)
    d = density_as_dict(result)
    col = next(c for c in d["columns"] if c["column"] == "age")
    assert "density" in col
    assert "empty_cells" in col


def test_register_density_args():
    parser = argparse.ArgumentParser()
    register_density_args(parser)
    args = parser.parse_args([])
    assert args.density is False
    assert args.density_json is False


def test_maybe_print_density_no_flag(rows, capsys):
    parser = argparse.ArgumentParser()
    register_density_args(parser)
    args = parser.parse_args([])
    result = maybe_print_density(args, rows)
    assert result is None
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_print_density_text_flag(rows, capsys):
    parser = argparse.ArgumentParser()
    register_density_args(parser)
    args = parser.parse_args(["--density"])
    result = maybe_print_density(args, rows)
    assert result is not None
    captured = capsys.readouterr()
    assert "Rows:" in captured.out


def test_maybe_print_density_json_flag(rows, capsys):
    parser = argparse.ArgumentParser()
    register_density_args(parser)
    args = parser.parse_args(["--density-json"])
    maybe_print_density(args, rows)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "total_rows" in data
