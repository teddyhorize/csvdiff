"""Tests for csvdiff.cli_rename."""
import argparse
import pytest
from csvdiff.cli_rename import (
    register_rename_args,
    rename_options_from_args,
    maybe_apply_renames,
)
from csvdiff.rename import RenameOptions


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_rename_args(p)
    return p


def test_register_rename_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "rename")
    assert args.rename == []


def test_register_rename_accepts_pairs(parser):
    args = parser.parse_args(["--rename", "a:b", "--rename", "c:d"])
    assert args.rename == ["a:b", "c:d"]


def test_rename_options_from_args_empty(parser):
    args = parser.parse_args([])
    opts = rename_options_from_args(args)
    assert opts.mapping == {}


def test_rename_options_from_args_with_pairs(parser):
    args = parser.parse_args(["--rename", "old:new"])
    opts = rename_options_from_args(args)
    assert opts.mapping == {"old": "new"}


def test_rename_options_from_args_multiple_pairs(parser):
    args = parser.parse_args(["--rename", "a:b", "--rename", "c:d"])
    opts = rename_options_from_args(args)
    assert opts.mapping == {"a": "b", "c": "d"}


def test_rename_options_from_args_invalid_raises(parser):
    args = parser.parse_args(["--rename", "badpair"])
    with pytest.raises(SystemExit, match="rename error"):
        rename_options_from_args(args)


def test_rename_options_from_args_empty_key_raises(parser):
    """A pair like ':new' has an empty key and should be rejected."""
    args = parser.parse_args(["--rename", ":new"])
    with pytest.raises(SystemExit, match="rename error"):
        rename_options_from_args(args)


def test_maybe_apply_renames_no_mapping():
    opts = RenameOptions()
    a = [{"x": "1"}]
    b = [{"x": "2"}]
    ra, rb = maybe_apply_renames(a, b, opts)
    assert ra is a
    assert rb is b


def test_maybe_apply_renames_with_mapping():
    opts = RenameOptions(mapping={"x": "y"})
    a = [{"x": "1"}]
    b = [{"x": "2"}]
    ra, rb = maybe_apply_renames(a, b, opts)
    assert ra == [{"y": "1"}]
    assert rb == [{"y": "2"}]
