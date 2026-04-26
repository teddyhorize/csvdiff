"""Tests for csvdiff.cli_outlier."""
from __future__ import annotations

import argparse
import json

import pytest

from csvdiff.cli_outlier import (
    maybe_print_outliers,
    outlier_as_dict,
    register_outlier_args,
)
from csvdiff.outlier import detect_outliers


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_outlier_args(p)
    return p


@pytest.fixture
def rows():
    return [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "11"},
        {"name": "c", "score": "12"},
        {"name": "d", "score": "99"},
    ]


def test_register_outlier_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "outlier_column")
    assert hasattr(args, "outlier_z")
    assert hasattr(args, "outlier_json")


def test_outlier_column_default_none(parser):
    args = parser.parse_args([])
    assert args.outlier_column is None


def test_outlier_z_default(parser):
    args = parser.parse_args([])
    assert args.outlier_z == 2.5


def test_outlier_json_default_false(parser):
    args = parser.parse_args([])
    assert args.outlier_json is False


def test_maybe_print_outliers_no_column(parser, rows):
    args = parser.parse_args([])
    result = maybe_print_outliers(args, rows)
    assert result is None


def test_maybe_print_outliers_returns_result(parser, rows, capsys):
    args = parser.parse_args(["--outlier-column", "score"])
    result = maybe_print_outliers(args, rows)
    assert result is not None
    assert result.column == "score"


def test_maybe_print_outliers_prints_text(parser, rows, capsys):
    args = parser.parse_args(["--outlier-column", "score"])
    maybe_print_outliers(args, rows)
    out = capsys.readouterr().out
    assert "score" in out


def test_maybe_print_outliers_json_output(parser, rows, capsys):
    args = parser.parse_args(["--outlier-column", "score", "--outlier-json"])
    maybe_print_outliers(args, rows)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["column"] == "score"
    assert "outlier_count" in data


def test_outlier_as_dict_keys(rows):
    result = detect_outliers(rows, column="score")
    d = outlier_as_dict(result)
    assert set(d.keys()) == {
        "column", "mean", "stdev", "threshold", "outlier_count", "outliers"
    }


def test_outlier_as_dict_values(rows):
    result = detect_outliers(rows, column="score")
    d = outlier_as_dict(result)
    assert d["column"] == "score"
    assert isinstance(d["outliers"], list)
