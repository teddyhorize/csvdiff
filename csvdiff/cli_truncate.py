"""CLI helpers for truncation options."""

import argparse
from csvdiff.truncate import TruncateOptions, TruncateError


def register_truncate_args(parser: argparse.ArgumentParser) -> None:
    """Add truncation-related arguments to an ArgumentParser."""
    grp = parser.add_argument_group("truncation")
    grp.add_argument(
        "--max-rows",
        type=int,
        default=0,
        metavar="N",
        help="Limit output to N rows per section (0 = no limit).",
    )
    grp.add_argument(
        "--max-cols",
        type=int,
        default=0,
        metavar="N",
        help="Limit output to first N columns (0 = no limit).",
    )
    grp.add_argument(
        "--max-cell-len",
        type=int,
        default=0,
        metavar="N",
        help="Truncate cell values to N characters (0 = no limit).",
    )


def build_truncate_options(args: argparse.Namespace) -> TruncateOptions:
    """Build TruncateOptions from parsed CLI args.

    Raises:
        TruncateError: If any truncation limit is negative.
    """
    max_rows = getattr(args, "max_rows", 0)
    max_cols = getattr(args, "max_cols", 0)
    max_cell_len = getattr(args, "max_cell_len", 0)

    invalid = [
        ("--max-rows", max_rows),
        ("--max-cols", max_cols),
        ("--max-cell-len", max_cell_len),
    ]
    for flag, value in invalid:
        if value < 0:
            raise TruncateError(
                f"{flag} must be a non-negative integer, got {value}."
            )

    return TruncateOptions(
        max_rows=max_rows,
        max_cols=max_cols,
        max_cell_len=max_cell_len,
    )


def truncate_options_from_args(args: argparse.Namespace) -> TruncateOptions:
    """Convenience wrapper used by the main CLI entry point."""
    return build_truncate_options(args)
