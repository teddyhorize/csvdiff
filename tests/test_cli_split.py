"""Tests for csvdiff.cli_split."""

from __future__ import annotations

import argparse
import pytest
from unittest.mock import patch, MagicMock

from csvdiff.cli_split import (
    register_split_args,
    split_options_from_args,
    maybe_apply_split,
)
from csvdiff.differ import DiffResult


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    register_split_args(p)
    return p


@pytest.fixture()
def diff_result():
    return DiffResult(
        added_rows=[{"id": "1", "name": "Alice"}],
        removed_rows=[],
        modified_rows=[],
        unchanged_rows=[],
    )


def test_register_split_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "split_output_dir")


def test_register_split_prefix_default(parser):
    args = parser.parse_args([])
    assert args.split_prefix == "diff"


def test_register_split_include_unchanged_default(parser):
    args = parser.parse_args([])
    assert args.split_include_unchanged is False


def test_split_options_none_when_no_dir(parser):
    args = parser.parse_args([])
    assert split_options_from_args(args) is None


def test_split_options_returns_options_when_dir_set(parser):
    args = parser.parse_args(["--split-output-dir", "/tmp"])
    opts = split_options_from_args(args)
    assert opts is not None
    assert opts.output_dir == "/tmp"


def test_split_options_prefix_forwarded(parser):
    args = parser.parse_args(["--split-output-dir", "/tmp", "--split-prefix", "out"])
    opts = split_options_from_args(args)
    assert opts.prefix == "out"


def test_split_options_include_unchanged_forwarded(parser):
    args = parser.parse_args(
        ["--split-output-dir", "/tmp", "--split-include-unchanged"]
    )
    opts = split_options_from_args(args)
    assert opts.include_unchanged is True


def test_maybe_apply_split_returns_none_when_no_dir(parser, diff_result):
    args = parser.parse_args([])
    result = maybe_apply_split(args, diff_result, ["id", "name"])
    assert result is None


def test_maybe_apply_split_calls_split_diff(tmp_path, parser, diff_result):
    args = parser.parse_args(["--split-output-dir", str(tmp_path)])
    with patch("csvdiff.cli_split.split_diff") as mock_split:
        mock_split.return_value = MagicMock(files_written=[])
        with patch("builtins.print"):
            maybe_apply_split(args, diff_result, ["id", "name"])
        mock_split.assert_called_once()
