"""Tests for csvdiff.cli_timeline."""
from __future__ import annotations

import argparse
import json
from io import StringIO
from unittest.mock import patch

import pytest

from csvdiff.differ import DiffResult
from csvdiff.timeline import Timeline, add_entry
from csvdiff.cli_timeline import (
    register_timeline_args,
    timeline_as_dict,
    maybe_print_timeline,
)


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_timeline_args(p)
    return p


@pytest.fixture()
def sample_timeline() -> Timeline:
    tl = Timeline()
    result = DiffResult(
        added=[{"id": "1"}],
        removed=[],
        modified=[],
        added_columns=["score"],
        removed_columns=[],
    )
    add_entry(tl, result, label="sprint-42", timestamp="2024-03-01T10:00:00Z")
    return tl


# ---------------------------------------------------------------------------
# register_timeline_args
# ---------------------------------------------------------------------------

def test_register_timeline_args_flag(parser):
    args = parser.parse_args([])
    assert args.timeline is False


def test_register_timeline_label_default(parser):
    args = parser.parse_args([])
    assert args.timeline_label == ""


def test_register_timeline_json_flag(parser):
    args = parser.parse_args(["--timeline-json"])
    assert args.timeline_json is True


# ---------------------------------------------------------------------------
# timeline_as_dict
# ---------------------------------------------------------------------------

def test_timeline_as_dict_has_entries_key(sample_timeline):
    d = timeline_as_dict(sample_timeline)
    assert "entries" in d


def test_timeline_as_dict_entry_keys(sample_timeline):
    entry = timeline_as_dict(sample_timeline)["entries"][0]
    for key in ("timestamp", "label", "added", "removed", "modified",
                "added_columns", "removed_columns", "total_changes", "is_clean"):
        assert key in entry, f"missing key: {key}"


def test_timeline_as_dict_values(sample_timeline):
    entry = timeline_as_dict(sample_timeline)["entries"][0]
    assert entry["label"] == "sprint-42"
    assert entry["added"] == 1
    assert entry["added_columns"] == ["score"]


# ---------------------------------------------------------------------------
# maybe_print_timeline
# ---------------------------------------------------------------------------

def test_maybe_print_timeline_no_flag(sample_timeline, capsys):
    args = argparse.Namespace(timeline=False, timeline_json=False)
    maybe_print_timeline(args, sample_timeline)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_print_timeline_plain(sample_timeline, capsys):
    args = argparse.Namespace(timeline=True, timeline_json=False)
    maybe_print_timeline(args, sample_timeline)
    captured = capsys.readouterr()
    assert "sprint-42" in captured.out


def test_maybe_print_timeline_json(sample_timeline, capsys):
    args = argparse.Namespace(timeline=True, timeline_json=True)
    maybe_print_timeline(args, sample_timeline)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["entries"][0]["label"] == "sprint-42"
