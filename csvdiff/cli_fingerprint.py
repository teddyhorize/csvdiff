"""CLI helpers for the fingerprint feature."""
from __future__ import annotations

import argparse
import json
from typing import List, Dict, Optional

from csvdiff.fingerprint import Fingerprint, compute_fingerprint, format_fingerprint
from csvdiff.differ import DiffResult


def register_fingerprint_args(parser: argparse.ArgumentParser) -> None:
    """Add fingerprint-related arguments to an argument parser."""
    group = parser.add_argument_group("fingerprint")
    group.add_argument(
        "--fingerprint",
        action="store_true",
        default=False,
        help="Compute and display a content fingerprint for both files.",
    )
    group.add_argument(
        "--fingerprint-json",
        action="store_true",
        default=False,
        help="Output fingerprint as JSON.",
    )


def fingerprint_as_dict(fp: Fingerprint) -> dict:
    """Serialize a Fingerprint to a plain dict."""
    return {
        "left_hash": fp.left_hash,
        "right_hash": fp.right_hash,
        "diff_hash": fp.diff_hash,
        "row_count_left": fp.row_count_left,
        "row_count_right": fp.row_count_right,
        "is_identical": fp.is_identical,
    }


def maybe_print_fingerprint(
    args: argparse.Namespace,
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    result: DiffResult,
    *,
    color: bool = False,
) -> Optional[Fingerprint]:
    """Compute and print the fingerprint if --fingerprint was requested."""
    if not getattr(args, "fingerprint", False):
        return None

    fp = compute_fingerprint(left, right, result)

    if getattr(args, "fingerprint_json", False):
        print(json.dumps(fingerprint_as_dict(fp), indent=2))
    else:
        print(format_fingerprint(fp, color=color))

    return fp
