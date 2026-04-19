"""Tests for csvdiff.cli_score."""
import argparse
import json
from io import StringIO
import pytest
from csvdiff.differ import DiffResult
from csvdiff.cli_score import register_score_args, maybe_print_score, score_as_dict
from csvdiff.score import compute_score


def _parser():
    p = argparse.ArgumentParser()
    register_score_args(p)
    return p


def _result(unchanged=None, added=None):
    return DiffResult(
        added=added or {},
        removed={},
        modified={},
        unchanged=unchanged or {},
        added_columns=[],
        removed_columns=[],
    )


def test_register_score_args():
    p = _parser()
    args = p.parse_args([])
    assert hasattr(args, "score")
    assert hasattr(args, "score_json")


def test_score_flag_default_false():
    p = _parser()
    args = p.parse_args([])
    assert args.score is False
    assert args.score_json is False


def test_score_as_dict_keys():
    r = _result(unchanged={"a": {}})
    s = compute_score(r)
    d = score_as_dict(s)
    assert set(d.keys()) == {"score", "total_rows", "matched_rows", "added", "removed", "modified"}


def test_maybe_print_score_skips_when_not_set(capsys):
    p = _parser()
    args = p.parse_args([])
    maybe_print_score(args, _result())
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_print_score_text(capsys):
    p = _parser()
    args = p.parse_args(["--score"])
    maybe_print_score(args, _result(unchanged={"a": {}}, added={"b": {}}))
    captured = capsys.readouterr()
    assert "Similarity Score" in captured.out


def test_maybe_print_score_json(capsys):
    p = _parser()
    args = p.parse_args(["--score-json"])
    maybe_print_score(args, _result(unchanged={"a": {}}))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "score" in data
    assert data["score"] == 1.0
