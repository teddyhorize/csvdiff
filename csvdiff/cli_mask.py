"""CLI helpers for the mask feature."""
from __future__ import annotations

import argparse
from typing import List, Optional

from csvdiff.mask import MaskOptions, mask_rows


def register_mask_args(parser: argparse.ArgumentParser) -> None:
    """Attach mask-related arguments to *parser*."""
    parser.add_argument(
        "--mask",
        metavar="COLUMN",
        dest="mask_columns",
        nargs="+",
        default=[],
        help="Columns whose values should be masked before display.",
    )
    parser.add_argument(
        "--mask-placeholder",
        default="***",
        metavar="TEXT",
        help="Replacement text used when masking (default: ***).",
    )
    parser.add_argument(
        "--mask-keep-start",
        type=int,
        default=0,
        metavar="N",
        help="Number of leading characters to preserve (default: 0).",
    )
    parser.add_argument(
        "--mask-keep-end",
        type=int,
        default=0,
        metavar="N",
        help="Number of trailing characters to preserve (default: 0).",
    )


def mask_options_from_args(args: argparse.Namespace) -> Optional[MaskOptions]:
    """Build a :class:`MaskOptions` from parsed CLI arguments, or *None*."""
    columns: List[str] = getattr(args, "mask_columns", []) or []
    if not columns:
        return None
    return MaskOptions(
        columns=columns,
        placeholder=getattr(args, "mask_placeholder", "***"),
        keep_start=getattr(args, "mask_keep_start", 0),
        keep_end=getattr(args, "mask_keep_end", 0),
    )


def maybe_apply_mask(rows, args: argparse.Namespace):
    """Apply masking to *rows* if mask columns are configured."""
    opts = mask_options_from_args(args)
    if opts is None:
        return rows
    return mask_rows(rows, opts)
