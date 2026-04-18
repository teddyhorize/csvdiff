"""CLI helpers for building IgnoreOptions from parsed arguments."""

from typing import Optional, List
from csvdiff.ignore import IgnoreOptions, IgnoreError, apply_ignores


def build_ignore_options(
    ignore_columns: Optional[List[str]] = None,
    ignore_pattern: Optional[str] = None,
) -> IgnoreOptions:
    """Construct IgnoreOptions from CLI argument values."""
    return IgnoreOptions(
        columns=ignore_columns or [],
        row_pattern=ignore_pattern,
    )


def apply_ignore_to_pair(
    rows_a: List[dict],
    rows_b: List[dict],
    options: IgnoreOptions,
) -> tuple:
    """Apply ignore options to both sides of a diff pair."""
    return apply_ignores(rows_a, options), apply_ignores(rows_b, options)


def register_ignore_args(parser) -> None:
    """Register ignore-related CLI arguments onto an argparse parser."""
    parser.add_argument(
        "--ignore-columns",
        nargs="+",
        metavar="COL",
        default=[],
        help="Column names to exclude from comparison.",
    )
    parser.add_argument(
        "--ignore-pattern",
        metavar="REGEX",
        default=None,
        help="Skip rows whose values match this regex pattern.",
    )


def ignore_options_from_args(args) -> IgnoreOptions:
    """Extract IgnoreOptions from a parsed argparse Namespace."""
    return build_ignore_options(
        ignore_columns=getattr(args, "ignore_columns", []),
        ignore_pattern=getattr(args, "ignore_pattern", None),
    )
