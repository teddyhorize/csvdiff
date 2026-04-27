"""CLI helpers for frequency analysis output."""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from csvdiff.differ import DiffResult
from csvdiff.frequency import (
    FrequencyResult,
    compute_frequency,
    format_frequency,
)


def register_frequency_args(parser: argparse.ArgumentParser) -> None:
    """Register --frequency and related flags onto an existing parser."""
    parser.add_argument(
        "--frequency",
        metavar="COLUMN",
        nargs="*",
        default=None,
        help="Show value frequency for given columns (omit columns for all).",
    )
    parser.add_argument(
        "--frequency-top",
        type=int,
        default=5,
        metavar="N",
        help="Number of top values to display per column (default: 5).",
    )
    parser.add_argument(
        "--frequency-include-unchanged",
        action="store_true",
        default=False,
        help="Include unchanged rows in frequency counts.",
    )
    parser.add_argument(
        "--frequency-json",
        action="store_true",
        default=False,
        help="Output frequency data as JSON.",
    )


def frequency_as_dict(freq: FrequencyResult, top_n: int = 5) -> List[Dict[str, Any]]:
    """Serialise a FrequencyResult to a list of dicts."""
    out = []
    for cf in freq.columns:
        out.append(
            {
                "column": cf.column,
                "total": cf.total,
                "unique": cf.unique,
                "top": [{"value": v, "count": c} for v, c in cf.top(top_n)],
            }
        )
    return out


def maybe_print_frequency(
    args: argparse.Namespace,
    result: DiffResult,
) -> None:
    """Compute and print frequency stats if --frequency flag was supplied."""
    if args.frequency is None:
        return

    columns = args.frequency if args.frequency else None
    top_n: int = args.frequency_top
    include_unchanged: bool = args.frequency_include_unchanged
    as_json: bool = args.frequency_json

    freq = compute_frequency(result, columns=columns, include_unchanged=include_unchanged)

    if as_json:
        print(json.dumps(frequency_as_dict(freq, top_n), indent=2))
    else:
        print(format_frequency(freq, top_n=top_n))
