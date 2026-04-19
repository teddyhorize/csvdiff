"""Tests for csvdiff/cli_snapshot.py"""

import argparse
import pytest

from csvdiff.cli_snapshot import (
    DEFAULT_STORE,
    maybe_delete_snapshot,
    maybe_list_snapshots,
    maybe_save_snapshot,
    register_snapshot_args,
)
from csvdiff.snapshot import list_snapshots, load_snapshot


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_snapshot_args(p)
    return p


@pytest.fixture
def rows():
    return [{"id": "1", "val": "x"}]


def test_register_snapshot_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "snapshot_save")
    assert hasattr(args, "snapshot_list")
    assert hasattr(args, "snapshot_delete")
    assert hasattr(args, "snapshot_dir")


def test_default_store_value(parser):
    args = parser.parse_args([])
    assert args.snapshot_dir == DEFAULT_STORE


def test_maybe_save_snapshot_no_arg(parser, rows):
    args = parser.parse_args([])
    result = maybe_save_snapshot(args, ["id", "val"], rows, "f.csv")
    assert result is None


def test_maybe_save_snapshot_saves(parser, rows, tmp_path, capsys):
    store = str(tmp_path / "s")
    args = parser.parse_args(["--snapshot-save", "mysnap", "--snapshot-dir", store])
    snap = maybe_save_snapshot(args, ["id", "val"], rows, "f.csv")
    assert snap is not None
    assert snap.name == "mysnap"
    out = capsys.readouterr().out
    assert "mysnap" in out
    names = list_snapshots(store)
    assert "mysnap" in names


def test_maybe_list_snapshots_false_when_not_set(parser):
    args = parser.parse_args([])
    assert maybe_list_snapshots(args) is False


def test_maybe_list_snapshots_prints(parser, rows, tmp_path, capsys):
    store = str(tmp_path / "s")
    args_save = parser.parse_args(["--snapshot-save", "s1", "--snapshot-dir", store])
    maybe_save_snapshot(args_save, ["id"], rows, "f.csv")
    args_list = parser.parse_args(["--snapshot-list", "--snapshot-dir", store])
    result = maybe_list_snapshots(args_list)
    assert result is True
    assert "s1" in capsys.readouterr().out


def test_maybe_delete_snapshot_false_when_not_set(parser):
    args = parser.parse_args([])
    assert maybe_delete_snapshot(args) is False


def test_maybe_delete_snapshot_removes(parser, rows, tmp_path, capsys):
    store = str(tmp_path / "s")
    args_save = parser.parse_args(["--snapshot-save", "del_me", "--snapshot-dir", store])
    maybe_save_snapshot(args_save, ["id"], rows, "f.csv")
    args_del = parser.parse_args(["--snapshot-delete", "del_me", "--snapshot-dir", store])
    maybe_delete_snapshot(args_del)
    assert "del_me" not in list_snapshots(store)
