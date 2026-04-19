"""Tests for csvdiff/snapshot.py"""

import os
import pytest

from csvdiff.snapshot import (
    Snapshot,
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
    snapshot_from_rows,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "snaps")


@pytest.fixture
def sample_rows():
    return [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]


def test_snapshot_from_rows_basic(sample_rows):
    snap = snapshot_from_rows("test", "file.csv", ["id", "name"], sample_rows)
    assert snap.name == "test"
    assert snap.row_count == 2
    assert snap.headers == ["id", "name"]


def test_save_and_load_roundtrip(store, sample_rows):
    snap = snapshot_from_rows("mysnap", "a.csv", ["id", "name"], sample_rows)
    save_snapshot(store, snap)
    loaded = load_snapshot(store, "mysnap")
    assert loaded.name == "mysnap"
    assert loaded.row_count == 2
    assert loaded.headers == ["id", "name"]


def test_load_missing_raises(store):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(store, "ghost")


def test_list_empty(store):
    os.makedirs(store)
    assert list_snapshots(store) == []


def test_list_snapshots_returns_names(store, sample_rows):
    for name in ("alpha", "beta", "gamma"):
        snap = snapshot_from_rows(name, "f.csv", ["id"], sample_rows)
        save_snapshot(store, snap)
    names = list_snapshots(store)
    assert set(names) == {"alpha", "beta", "gamma"}


def test_delete_snapshot(store, sample_rows):
    snap = snapshot_from_rows("todel", "f.csv", ["id"], sample_rows)
    save_snapshot(store, snap)
    delete_snapshot(store, "todel")
    assert "todel" not in list_snapshots(store)


def test_delete_missing_raises(store):
    os.makedirs(store)
    with pytest.raises(SnapshotError):
        delete_snapshot(store, "nope")


def test_checksum_stored(store, sample_rows):
    snap = snapshot_from_rows("cs", "f.csv", ["id"], sample_rows, checksum="abc123")
    save_snapshot(store, snap)
    loaded = load_snapshot(store, "cs")
    assert loaded.checksum == "abc123"


def test_created_at_set(sample_rows):
    snap = snapshot_from_rows("t", "f.csv", ["id"], sample_rows)
    assert snap.created_at != ""
