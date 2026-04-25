"""CLI helpers for the cross-reference feature."""
from __future__ import annotations

import argparse
import json
from typing import Dict, List, Optional

from csvdiff.crossref import CrossRefResult, cross_reference, format_crossref


def register_crossref_args(parser: argparse.ArgumentParser) -> None:
    """Add cross-reference flags to an argument parser."""
    parser.add_argument(
        "--crossref",
        metavar="COLUMN",
        default=None,
        help="Cross-reference both files by this key column.",
    )
    parser.add_argument(
        "--crossref-json",
        action="store_true",
        default=False,
        help="Output cross-reference result as JSON.",
    )


def crossref_options_from_args(args: argparse.Namespace) -> Optional[str]:
    """Return the key column string or None if not requested."""
    return getattr(args, "crossref", None)


def crossref_as_dict(result: CrossRefResult) -> Dict:
    return {
        "key_column": result.key_column,
        "in_both": result.in_both,
        "only_in_left": result.only_in_left,
        "only_in_right": result.only_in_right,
        "total_keys": result.total_keys,
    }


def maybe_print_crossref(
    args: argparse.Namespace,
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
) -> None:
    """Run and print cross-reference if requested via CLI args."""
    key_column = crossref_options_from_args(args)
    if not key_column:
        return

    result = cross_reference(left, right, key_column)
    use_json = getattr(args, "crossref_json", False)

    if use_json:
        print(json.dumps(crossref_as_dict(result), indent=2))
    else:
        print(format_crossref(result))
