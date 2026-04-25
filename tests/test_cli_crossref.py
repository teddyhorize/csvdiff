"""Tests for csvdiff.cli_crossref."""
from __future__ import annotations

import argparse
import json
from io import StringIO
from unittest.mock import patch

import pytest

from csvdiff.cli_crossref import (
    crossref_as_dict,
    crossref_options_from_args,
    maybe_print_crossref,
    register_crossref_args,
)
from csvdiff.crossref import CrossRefResult

LEFT = [{"id": "1", "val": "a"}, {"id": "2", "val": "b"}]
RIGHT = [{"id": "2", "val": "b"}, {"id": "3", "val": "c"}]


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_crossref_args(p)
    return p


def test_register_crossref_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "crossref")


def test_register_crossref_json_flag(parser):
    args = parser.parse_args([])
    assert hasattr(args, "crossref_json")


def test_crossref_flag_default_none(parser):
    args = parser.parse_args([])
    assert args.crossref is None


def test_crossref_json_default_false(parser):
    args = parser.parse_args([])
    assert args.crossref_json is False


def test_crossref_options_from_args_none(parser):
    args = parser.parse_args([])
    assert crossref_options_from_args(args) is None


def test_crossref_options_from_args_set(parser):
    args = parser.parse_args(["--crossref", "id"])
    assert crossref_options_from_args(args) == "id"


def test_crossref_as_dict_keys():
    result = CrossRefResult(
        key_column="id",
        in_both=["2"],
        only_in_left=["1"],
        only_in_right=["3"],
    )
    d = crossref_as_dict(result)
    assert set(d.keys()) == {"key_column", "in_both", "only_in_left", "only_in_right", "total_keys"}


def test_crossref_as_dict_values():
    result = CrossRefResult(
        key_column="id",
        in_both=["2"],
        only_in_left=["1"],
        only_in_right=["3"],
    )
    d = crossref_as_dict(result)
    assert d["total_keys"] == 3
    assert d["key_column"] == "id"


def test_maybe_print_crossref_no_arg(parser, capsys):
    args = parser.parse_args([])
    maybe_print_crossref(args, LEFT, RIGHT)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_print_crossref_text(parser, capsys):
    args = parser.parse_args(["--crossref", "id"])
    maybe_print_crossref(args, LEFT, RIGHT)
    captured = capsys.readouterr()
    assert "id" in captured.out


def test_maybe_print_crossref_json(parser, capsys):
    args = parser.parse_args(["--crossref", "id", "--crossref-json"])
    maybe_print_crossref(args, LEFT, RIGHT)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "key_column" in data
