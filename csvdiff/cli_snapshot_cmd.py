"""Standalone CLI entry point for snapshot management."""

from __future__ import annotations

import argparse
import sys

from csvdiff.cli_snapshot import (
    DEFAULT_STORE,
    maybe_delete_snapshot,
    maybe_list_snapshots,
    maybe_save_snapshot,
)
from csvdiff.parser import load_csv
from csvdiff.snapshot import load_snapshot


def build_snapshot_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvdiff-snapshot",
        description="Manage CSV snapshots for regression tracking.",
    )
    sub = p.add_subparsers(dest="command")

    save_p = sub.add_parser("save", help="Save a snapshot of a CSV file")
    save_p.add_argument("file", help="CSV file to snapshot")
    save_p.add_argument("name", help="Snapshot name")
    save_p.add_argument("--dir", default=DEFAULT_STORE, dest="snapshot_dir")

    sub.add_parser("list", help="List saved snapshots").add_argument(
        "--dir", default=DEFAULT_STORE, dest="snapshot_dir"
    )

    del_p = sub.add_parser("delete", help="Delete a snapshot")
    del_p.add_argument("name", help="Snapshot name to delete")
    del_p.add_argument("--dir", default=DEFAULT_STORE, dest="snapshot_dir")

    show_p = sub.add_parser("show", help="Show snapshot metadata")
    show_p.add_argument("name")
    show_p.add_argument("--dir", default=DEFAULT_STORE, dest="snapshot_dir")

    return p


def main(argv=None) -> int:
    parser = build_snapshot_parser()
    args = parser.parse_args(argv)

    if args.command == "save":
        headers, rows = load_csv(args.file)
        import types
        ns = types.SimpleNamespace(
            snapshot_save=args.name,
            snapshot_dir=args.snapshot_dir,
        )
        maybe_save_snapshot(ns, headers, rows, args.file)

    elif args.command == "list":
        import types
        ns = types.SimpleNamespace(snapshot_list=True, snapshot_dir=args.snapshot_dir)
        maybe_list_snapshots(ns)

    elif args.command == "delete":
        import types
        ns = types.SimpleNamespace(snapshot_delete=args.name, snapshot_dir=args.snapshot_dir)
        maybe_delete_snapshot(ns)

    elif args.command == "show":
        snap = load_snapshot(args.snapshot_dir, args.name)
        print(f"Name:      {snap.name}")
        print(f"File:      {snap.path}")
        print(f"Rows:      {snap.row_count}")
        print(f"Headers:   {', '.join(snap.headers)}")
        print(f"Created:   {snap.created_at}")
        if snap.checksum:
            print(f"Checksum:  {snap.checksum}")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
