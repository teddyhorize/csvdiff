"""Tests for csvdiff.cli_highlight."""
import argparse
import io
import pytest

from csvdiff.cli_highlight import (
    register_highlight_args,
    print_highlights,
    maybe_print_highlights,
)
from csvdiff.differ import DiffResult


def _make_diff(modified=None):
    return DiffResult(
        added=[],
        removed=[],
        modified=modified or {},
        added_columns=[],
        removed_columns=[],
    )


def test_register_highlight_args():
    parser = argparse.ArgumentParser()
    register_highlight_args(parser)
    args = parser.parse_args(["--highlight"])
    assert args.highlight is True
    assert args.no_color is False


def test_register_no_color_flag():
    parser = argparse.ArgumentParser()
    register_highlight_args(parser)
    args = parser.parse_args(["--no-color"])
    assert args.no_color is True


def test_print_highlights_no_changes():
    buf = io.StringIO()
    diff = _make_diff()
    print_highlights(diff, use_color=False, out=buf)
    assert "No cell-level" in buf.getvalue()


def test_print_highlights_with_changes():
    buf = io.StringIO()
    diff = _make_diff(
        modified={
            "1": (
                {"id": "1", "val": "old"},
                {"id": "1", "val": "new"},
            )
        }
    )
    print_highlights(diff, use_color=False, out=buf)
    output = buf.getvalue()
    assert "old" in output
    assert "new" in output


def test_maybe_print_highlights_skipped_when_flag_off():
    buf = io.StringIO()
    args = argparse.Namespace(highlight=False, no_color=False)
    diff = _make_diff(modified={"1": ({"id": "1", "x": "a"}, {"id": "1", "x": "b"})})
    maybe_print_highlights(args, diff, out=buf)
    assert buf.getvalue() == ""


def test_maybe_print_highlights_runs_when_flag_on():
    buf = io.StringIO()
    args = argparse.Namespace(highlight=True, no_color=True)
    diff = _make_diff(modified={"1": ({"id": "1", "x": "a"}, {"id": "1", "x": "b"})})
    maybe_print_highlights(args, diff, out=buf)
    assert len(buf.getvalue()) > 0
