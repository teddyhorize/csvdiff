"""Tests for csvdiff.cli_correlation."""
import argparse
import json
import pytest
from csvdiff.cli_correlation import (
    register_correlation_args,
    correlation_as_dict,
    maybe_print_correlation,
)
from csvdiff.correlation import compute_correlation


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_correlation_args(p)
    return p


@pytest.fixture
def rows():
    return [
        {"x": "1", "y": "2"},
        {"x": "2", "y": "4"},
        {"x": "3", "y": "6"},
    ]


def test_register_correlation_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "correlate")
    assert hasattr(args, "correlate_all")
    assert hasattr(args, "correlation_json")
    assert hasattr(args, "correlation_precision")


def test_correlate_default_none(parser):
    args = parser.parse_args([])
    assert args.correlate is None


def test_correlate_all_default_false(parser):
    args = parser.parse_args([])
    assert args.correlate_all is False


def test_correlation_precision_default(parser):
    args = parser.parse_args([])
    assert args.correlation_precision == 4


def test_correlation_as_dict_keys(rows):
    result = compute_correlation(rows, columns=["x", "y"])
    d = correlation_as_dict(result)
    assert "columns" in d
    assert "pairs" in d


def test_correlation_as_dict_columns(rows):
    result = compute_correlation(rows, columns=["x", "y"])
    d = correlation_as_dict(result)
    assert set(d["columns"]) == {"x", "y"}


def test_maybe_print_correlation_no_flags_returns_none(parser, rows):
    args = parser.parse_args([])
    assert maybe_print_correlation(args, rows) is None


def test_maybe_print_correlation_with_columns(parser, rows, capsys):
    args = parser.parse_args(["--correlate", "x", "y"])
    result = maybe_print_correlation(args, rows)
    assert result is not None
    captured = capsys.readouterr()
    assert "x" in captured.out


def test_maybe_print_correlation_json_output(parser, rows, capsys):
    args = parser.parse_args(["--correlate", "x", "y", "--correlation-json"])
    maybe_print_correlation(args, rows)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "pairs" in data


def test_maybe_print_correlation_all_flag(parser, rows, capsys):
    args = parser.parse_args(["--correlate-all"])
    result = maybe_print_correlation(args, rows)
    assert result is not None
    assert set(result.columns) == {"x", "y"}
