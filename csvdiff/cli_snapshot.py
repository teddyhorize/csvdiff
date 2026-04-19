"""CLI helpers for snapshot save/load/list/delete commands."""

from __future__ import annotations

import argparse
from typing import List, Optional

from csvdiff.snapshot import (
    Snapshot,
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
    snapshot_from_rows,
)


DEFAULT_STORE = ".csvdiff_snapshots"


def register_snapshot_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--snapshot-save", metavar="NAME", help="Save a snapshot with this name")
    parser.add_argument("--snapshot-compare", metavar="NAME", help="Compare current file against saved snapshot")
    parser.add_argument("--snapshot-list", action="store_true", help="List saved snapshots")
    parser.add_argument("--snapshot-delete", metavar="NAME", help="Delete a named snapshot")
    parser.add_argument("--snapshot-dir", default=DEFAULT_STORE, metavar="DIR", help="Directory for snapshots")


def maybe_save_snapshot(
    args: argparse.Namespace,
    headers: List[str],
    rows: list,
    file_path: str,
    checksum: str = "",
) -> Optional[Snapshot]:
    name = getattr(args, "snapshot_save", None)
    if not name:
        return None
    store = getattr(args, "snapshot_dir", DEFAULT_STORE)
    snap = snapshot_from_rows(name, file_path, headers, rows, checksum)
    save_snapshot(store, snap)
    print(f"Snapshot '{name}' saved.")
    return snap


def maybe_list_snapshots(args: argparse.Namespace) -> bool:
    if not getattr(args, "snapshot_list", False):
        return False
    store = getattr(args, "snapshot_dir", DEFAULT_STORE)
    names = list_snapshots(store)
    if not names:
        print("No snapshots found.")
    else:
        for n in sorted(names):
            print(n)
    return True


def maybe_delete_snapshot(args: argparse.Namespace) -> bool:
    name = getattr(args, "snapshot_delete", None)
    if not name:
        return False
    store = getattr(args, "snapshot_dir", DEFAULT_STORE)
    try:
        delete_snapshot(store, name)
        print(f"Snapshot '{name}' deleted.")
    except SnapshotError as e:
        print(f"Error: {e}")
    return True
