"""CLI helpers for the split feature."""

from __future__ import annotations

import argparse
from typing import Optional

from csvdiff.split import SplitOptions, SplitResult, split_diff, format_split_result
from csvdiff.differ import DiffResult


def register_split_args(parser: argparse.ArgumentParser) -> None:
    """Add split-related arguments to an argument parser."""
    grp = parser.add_argument_group("split output")
    grp.add_argument(
        "--split-output-dir",
        metavar="DIR",
        default=None,
        help="Directory to write split CSV files into.",
    )
    grp.add_argument(
        "--split-prefix",
        metavar="PREFIX",
        default="diff",
        help="Filename prefix for split output files (default: diff).",
    )
    grp.add_argument(
        "--split-include-unchanged",
        action="store_true",
        default=False,
        help="Also write unchanged rows to a separate file.",
    )


def split_options_from_args(args: argparse.Namespace) -> Optional[SplitOptions]:
    """Build SplitOptions from parsed CLI args, or None if not requested."""
    if not getattr(args, "split_output_dir", None):
        return None
    return SplitOptions(
        output_dir=args.split_output_dir,
        prefix=getattr(args, "split_prefix", "diff"),
        include_unchanged=getattr(args, "split_include_unchanged", False),
    )


def maybe_apply_split(
    args: argparse.Namespace,
    result: DiffResult,
    headers: list,
) -> Optional[SplitResult]:
    """Apply split if requested; print summary and return result."""
    opts = split_options_from_args(args)
    if opts is None:
        return None
    split_result = split_diff(result, headers, opts)
    print(format_split_result(split_result))
    return split_result
