"""CLI helpers for column reordering."""

import argparse
from typing import Optional, List

from csvdiff.reorder import ReorderOptions, reorder_rows, ReorderError


def register_reorder_args(parser: argparse.ArgumentParser) -> None:
    """Add reorder-related arguments to an argument parser."""
    parser.add_argument(
        "--reorder",
        nargs="+",
        metavar="COL",
        default=None,
        help="Specify exact column order (unlisted columns appended at end).",
    )
    parser.add_argument(
        "--move-to-front",
        nargs="+",
        metavar="COL",
        default=None,
        help="Move these columns to the front.",
    )
    parser.add_argument(
        "--move-to-back",
        nargs="+",
        metavar="COL",
        default=None,
        help="Move these columns to the back.",
    )


def reorder_options_from_args(args: argparse.Namespace) -> Optional[ReorderOptions]:
    """Build ReorderOptions from parsed args, or None if no reorder requested."""
    columns = getattr(args, "reorder", None) or []
    front = getattr(args, "move_to_front", None) or []
    back = getattr(args, "move_to_back", None) or []
    if not columns and not front and not back:
        return None
    return ReorderOptions(columns=columns, move_to_front=front, move_to_back=back)


def maybe_apply_reorder(
    rows: List[dict],
    headers: List[str],
    args: argparse.Namespace,
) -> tuple:
    """Apply reordering if options are present; return (headers, rows) unchanged otherwise."""
    options = reorder_options_from_args(args)
    if options is None:
        return headers, rows
    return reorder_rows(rows, headers, options)
