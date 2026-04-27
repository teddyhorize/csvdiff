"""Tests for csvdiff.cli_drift."""
import argparse
import json
from io import StringIO
from unittest.mock import patch

import pytest

from csvdiff.differ import DiffResult
from csvdiff.drift import detect_drift
from csvdiff.cli_drift import (
    drift_as_dict,
    maybe_print_drift,
    register_drift_args,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    register_drift_args(p)
    return p


def _simple_report():
    result = DiffResult(
        added=[{"id": "9"}],
        removed=[],
        modified=[],
        added_columns=[],
        removed_columns=[],
    )
    return detect_drift(["id", "name"], ["id", "name"], result, label="test")


# ---------------------------------------------------------------------------
# register_drift_args
# ---------------------------------------------------------------------------

def test_register_drift_args_flag(parser):
    args = parser.parse_args([])
    assert args.drift is False


def test_register_drift_label_default(parser):
    args = parser.parse_args([])
    assert args.drift_label == ""


def test_register_drift_json_default(parser):
    args = parser.parse_args([])
    assert args.drift_json is False


def test_register_drift_flag_set(parser):
    args = parser.parse_args(["--drift"])
    assert args.drift is True


# ---------------------------------------------------------------------------
# drift_as_dict
# ---------------------------------------------------------------------------

def test_drift_as_dict_keys():
    report = _simple_report()
    d = drift_as_dict(report)
    assert "has_drift" in d
    assert "added_rows" in d
    assert "removed_rows" in d
    assert "modified_rows" in d
    assert "schema_drift" in d


def test_drift_as_dict_has_drift_true():
    report = _simple_report()
    assert drift_as_dict(report)["has_drift"] is True


def test_drift_as_dict_schema_keys():
    report = _simple_report()
    sd = drift_as_dict(report)["schema_drift"]
    assert "added_columns" in sd
    assert "removed_columns" in sd
    assert "reordered" in sd


# ---------------------------------------------------------------------------
# maybe_print_drift
# ---------------------------------------------------------------------------

def test_maybe_print_drift_skips_when_flag_false(parser, capsys):
    args = parser.parse_args([])
    report = _simple_report()
    maybe_print_drift(args, report)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_print_drift_prints_text(parser, capsys):
    args = parser.parse_args(["--drift"])
    report = _simple_report()
    maybe_print_drift(args, report)
    captured = capsys.readouterr()
    assert "drift" in captured.out.lower() or "Added" in captured.out


def test_maybe_print_drift_json_output(parser, capsys):
    args = parser.parse_args(["--drift", "--drift-json"])
    report = _simple_report()
    maybe_print_drift(args, report)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["has_drift"] is True


def test_maybe_print_drift_none_report(parser, capsys):
    args = parser.parse_args(["--drift"])
    maybe_print_drift(args, None)
    assert capsys.readouterr().out == ""
