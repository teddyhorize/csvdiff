"""CLI helpers for diff context feature."""

from __future__ import annotations

import argparse
from typing import List, Dict, Any, Optional

from csvdiff.diff_context import ContextOptions, ContextWindow, build_context_windows, format_context
from csvdiff.differ import DiffResult


def register_context_args(parser: argparse.ArgumentParser) -> None:
    """Add --context / --context-lines flags to *parser*."""
    parser.add_argument(
        "--context",
        action="store_true",
        default=False,
        help="Show surrounding context rows for each changed row.",
    )
    parser.add_argument(
        "--context-lines",
        type=int,
        default=2,
        metavar="N",
        help="Number of context rows to show before/after each change (default: 2).",
    )


def context_options_from_args(args: argparse.Namespace) -> Optional[ContextOptions]:
    """Return ContextOptions if --context was requested, else None."""
    if not getattr(args, "context", False):
        return None
    return ContextOptions(lines=getattr(args, "context_lines", 2))


def maybe_print_context(
    args: argparse.Namespace,
    rows: List[Dict[str, Any]],
    result: DiffResult,
    key_column: str,
) -> None:
    """Print context windows if --context flag is set."""
    opts = context_options_from_args(args)
    if opts is None:
        return
    windows = build_context_windows(rows, result, key_column, opts)
    print(format_context(windows, key_column))
