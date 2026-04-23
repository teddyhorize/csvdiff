"""CLI helpers for the aggregate feature."""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List, Optional

from csvdiff.aggregate import (
    AggregateOptions,
    AggregateResult,
    aggregate_diff,
    format_aggregate,
)
from csvdiff.differ import DiffResult


def register_aggregate_args(parser: argparse.ArgumentParser) -> None:
    """Add --aggregate and related flags to an argument parser."""
    parser.add_argument(
        "--aggregate",
        metavar="COL",
        nargs="+",
        default=None,
        help="Aggregate numeric values in these columns across changed rows.",
    )
    parser.add_argument(
        "--aggregate-json",
        action="store_true",
        default=False,
        help="Output aggregate results as JSON.",
    )


def aggregate_options_from_args(args: argparse.Namespace) -> Optional[AggregateOptions]:
    columns = getattr(args, "aggregate", None)
    if not columns:
        return None
    return AggregateOptions(columns=columns)


def results_as_dicts(results: List[AggregateResult]) -> List[Dict[str, Any]]:
    return [
        {
            "column": r.column,
            "count": r.count,
            "total": r.total,
            "minimum": r.minimum,
            "maximum": r.maximum,
            "mean": r.mean,
        }
        for r in results
    ]


def maybe_print_aggregate(
    args: argparse.Namespace,
    result: DiffResult,
) -> None:
    opts = aggregate_options_from_args(args)
    if opts is None:
        return
    agg_results = aggregate_diff(result, opts)
    if getattr(args, "aggregate_json", False):
        print(json.dumps(results_as_dicts(agg_results), indent=2))
    else:
        print(format_aggregate(agg_results))
