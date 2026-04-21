"""Tests for csvdiff.lineage and csvdiff.cli_lineage."""
import argparse
import json
import pytest
from csvdiff.lineage import (
    LineageError,
    build_lineage,
    record_rename,
    record_filter,
    format_lineage,
)
from csvdiff.cli_lineage import (
    register_lineage_args,
    lineage_as_dict,
    maybe_print_lineage,
)


def test_build_lineage_basic():
    lin = build_lineage("file.csv")
    assert lin.source_file == "file.csv"
    assert lin.events == []


def test_build_lineage_empty_raises():
    with pytest.raises(LineageError):
        build_lineage("")


def test_record_rename_adds_event():
    lin = build_lineage("a.csv")
    record_rename(lin, {"old_col": "new_col"})
    assert len(lin.events) == 1
    ev = lin.events[0]
    assert ev.step == "rename"
    assert "old_col->new_col" in ev.affected_columns


def test_record_rename_multiple_columns():
    lin = build_lineage("a.csv")
    record_rename(lin, {"a": "b", "c": "d"})
    assert len(lin.events[0].affected_columns) == 2


def test_record_filter_adds_event():
    lin = build_lineage("a.csv")
    record_filter(lin, removed_rows=5, reason="limit applied")
    ev = lin.events[0]
    assert ev.step == "filter"
    assert ev.affected_rows == 5
    assert "limit applied" in ev.description


def test_record_filter_no_reason():
    lin = build_lineage("a.csv")
    record_filter(lin, removed_rows=2)
    assert "2" in lin.events[0].description


def test_format_lineage_no_events():
    lin = build_lineage("a.csv")
    output = format_lineage(lin)
    assert "no transformations" in output
    assert "a.csv" in output


def test_format_lineage_with_events():
    lin = build_lineage("a.csv")
    record_rename(lin, {"x": "y"})
    record_filter(lin, 3)
    output = format_lineage(lin)
    assert "rename" in output
    assert "filter" in output
    assert "x->y" in output


def test_register_lineage_args():
    parser = argparse.ArgumentParser()
    register_lineage_args(parser)
    args = parser.parse_args([])
    assert args.lineage is False
    assert args.lineage_json is False


def test_lineage_as_dict_structure():
    lin = build_lineage("f.csv")
    record_rename(lin, {"a": "b"})
    d = lineage_as_dict(lin)
    assert d["source_file"] == "f.csv"
    assert isinstance(d["events"], list)
    assert d["events"][0]["step"] == "rename"


def test_maybe_print_lineage_json(capsys):
    parser = argparse.ArgumentParser()
    register_lineage_args(parser)
    args = parser.parse_args(["--lineage-json"])
    lin = build_lineage("b.csv")
    record_filter(lin, 1)
    maybe_print_lineage(args, lin)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["source_file"] == "b.csv"


def test_maybe_print_lineage_text(capsys):
    parser = argparse.ArgumentParser()
    register_lineage_args(parser)
    args = parser.parse_args(["--lineage"])
    lin = build_lineage("c.csv")
    maybe_print_lineage(args, lin)
    captured = capsys.readouterr()
    assert "c.csv" in captured.out


def test_maybe_print_lineage_skips_when_none(capsys):
    parser = argparse.ArgumentParser()
    register_lineage_args(parser)
    args = parser.parse_args(["--lineage"])
    maybe_print_lineage(args, None)
    captured = capsys.readouterr()
    assert captured.out == ""
