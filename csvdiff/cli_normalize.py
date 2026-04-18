"""CLI helpers for registering and applying normalization arguments."""

from __future__ import annotations
import argparse
from typing import List, Dict

from csvdiff.normalize import NormalizeOptions, normalize_rows, normalize_options_from_args


def register_normalize_args(parser: argparse.ArgumentParser) -> None:
    """Add normalization-related arguments to an ArgumentParser."""
    grp = parser.add_argument_group("normalization")
    grp.add_argument(
        "--no-strip",
        action="store_true",
        default=False,
        help="Disable automatic whitespace stripping from cell values.",
    )
    grp.add_argument(
        "--normalize-lowercase",
        action="store_true",
        default=False,
        help="Lowercase all (or selected) cell values before comparison.",
    )
    grp.add_argument(
        "--normalize-columns",
        nargs="+",
        metavar="COL",
        default=[],
        help="Restrict normalization to these columns only.",
    )


def apply_normalize_to_pair(
    rows_a: List[Dict[str, str]],
    rows_b: List[Dict[str, str]],
    opts: NormalizeOptions,
) -> tuple:
    """Return (normalized_a, normalized_b) using the given options."""
    return normalize_rows(rows_a, opts), normalize_rows(rows_b, opts)


def build_normalize_options(args: argparse.Namespace) -> NormalizeOptions:
    return normalize_options_from_args(args)
