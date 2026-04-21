"""Tests for csvdiff.diff_context."""

from __future__ import annotations

import argparse
import pytest

from csvdiff.differ import DiffResult
from csvdiff.diff_context import (
    ContextError,
    ContextOptions,
    ContextWindow,
    build_context_windows,
    format_context,
)
from csvdiff.cli_diff_context import (
    register_context_args,
    context_options_from_args,
    maybe_print_context,
)


ROWS = [
    {"id": "1", "name": "Alice", "age": "30"},
    {"id": "2", "name": "Bob", "age": "25"},
    {"id": "3", "name": "Carol", "age": "28"},
    {"id": "4", "name": "Dave", "age": "35"},
    {"id": "5", "name": "Eve", "age": "22"},
]


@pytest.fixture
def clean_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified={}, added_columns=[], removed_columns=[])


@pytest.fixture
def dirty_result() -> DiffResult:
    return DiffResult(
        added=[{"id": "6", "name": "Frank", "age": "40"}],
        removed=[{"id": "1", "name": "Alice", "age": "30"}],
        modified={
            "3": {"old": {"id": "3", "name": "Carol", "age": "28"}, "new": {"id": "3", "name": "Carol", "age": "29"}}
        },
        added_columns=[],
        removed_columns=[],
    )


def test_build_context_empty_result(clean_result):
    windows = build_context_windows(ROWS, clean_result, "id", ContextOptions(lines=2))
    assert windows == []


def test_build_context_returns_windows(dirty_result):
    windows = build_context_windows(ROWS, dirty_result, "id", ContextOptions(lines=2))
    assert len(windows) == 3  # 1 added + 1 removed + 1 modified


def test_context_window_change_types(dirty_result):
    windows = build_context_windows(ROWS, dirty_result, "id", ContextOptions(lines=2))
    types = {w.change_type for w in windows}
    assert "added" in types
    assert "removed" in types
    assert "modified" in types


def test_context_before_and_after(dirty_result):
    windows = build_context_windows(ROWS, dirty_result, "id", ContextOptions(lines=1))
    removed_win = next(w for w in windows if w.change_type == "removed")
    # Row 0 (id=1) has no before rows, 1 after row
    assert len(removed_win.before) == 0
    assert len(removed_win.after) == 1


def test_context_lines_zero(dirty_result):
    windows = build_context_windows(ROWS, dirty_result, "id", ContextOptions(lines=0))
    for w in windows:
        assert w.before == []
        assert w.after == []


def test_validate_negative_lines_raises(dirty_result):
    with pytest.raises(ContextError):
        build_context_windows(ROWS, dirty_result, "id", ContextOptions(lines=-1))


def test_format_context_empty():
    output = format_context([], "id")
    assert "No changed rows" in output


def test_format_context_contains_key(dirty_result):
    windows = build_context_windows(ROWS, dirty_result, "id", ContextOptions(lines=1))
    output = format_context(windows, "id")
    assert "MODIFIED" in output or "REMOVED" in output or "ADDED" in output


def test_register_context_args():
    parser = argparse.ArgumentParser()
    register_context_args(parser)
    args = parser.parse_args(["--context", "--context-lines", "3"])
    assert args.context is True
    assert args.context_lines == 3


def test_context_options_from_args_not_set():
    parser = argparse.ArgumentParser()
    register_context_args(parser)
    args = parser.parse_args([])
    assert context_options_from_args(args) is None


def test_context_options_from_args_set():
    parser = argparse.ArgumentParser()
    register_context_args(parser)
    args = parser.parse_args(["--context", "--context-lines", "4"])
    opts = context_options_from_args(args)
    assert opts is not None
    assert opts.lines == 4
