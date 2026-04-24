"""Tests for csvdiff.cli_headermap."""
import argparse
import json

import pytest

from csvdiff.cli_headermap import (
    headermap_as_dict,
    maybe_print_header_map,
    register_headermap_args,
)
from csvdiff.headermap import build_header_mapping


@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_headermap_args(p)
    return p


# ---------------------------------------------------------------------------
# register_headermap_args
# ---------------------------------------------------------------------------

def test_register_adds_show_flag(parser):
    args = parser.parse_args([])
    assert hasattr(args, "show_header_map")
    assert args.show_header_map is False


def test_register_adds_no_fuzzy_flag(parser):
    args = parser.parse_args(["--no-fuzzy-headers"])
    assert args.no_fuzzy_headers is True


def test_register_adds_json_flag(parser):
    args = parser.parse_args(["--header-map-json"])
    assert args.header_map_json is True


# ---------------------------------------------------------------------------
# headermap_as_dict
# ---------------------------------------------------------------------------

def test_headermap_as_dict_keys():
    m = build_header_mapping(["id", "Name"], ["id", "name"])
    d = headermap_as_dict(m)
    assert set(d.keys()) == {"exact", "fuzzy", "unmapped_left", "unmapped_right"}


def test_headermap_as_dict_exact_values():
    m = build_header_mapping(["id"], ["id"])
    d = headermap_as_dict(m)
    assert d["exact"] == {"id": "id"}


# ---------------------------------------------------------------------------
# maybe_print_header_map
# ---------------------------------------------------------------------------

def test_returns_none_when_flag_not_set(parser, capsys):
    args = parser.parse_args([])
    result = maybe_print_header_map(args, ["id"], ["id"])
    assert result is None
    captured = capsys.readouterr()
    assert captured.out == ""


def test_returns_mapping_when_flag_set(parser, capsys):
    args = parser.parse_args(["--show-header-map"])
    result = maybe_print_header_map(args, ["id", "name"], ["id", "name"])
    assert result is not None
    assert "id" in result.exact


def test_prints_text_by_default(parser, capsys):
    args = parser.parse_args(["--show-header-map"])
    maybe_print_header_map(args, ["id"], ["id"])
    captured = capsys.readouterr()
    assert "Exact" in captured.out


def test_prints_json_when_requested(parser, capsys):
    args = parser.parse_args(["--show-header-map", "--header-map-json"])
    maybe_print_header_map(args, ["id"], ["id"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "exact" in data
