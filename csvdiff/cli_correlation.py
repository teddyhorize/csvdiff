"""CLI helpers for the correlation feature."""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List, Optional

from csvdiff.correlation import CorrelationResult, compute_correlation, format_correlation


def register_correlation_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--correlate",
        nargs="+",
        metavar="COLUMN",
        default=None,
        help="Compute Pearson correlation for the given columns.",
    )
    parser.add_argument(
        "--correlate-all",
        action="store_true",
        default=False,
        help="Compute Pearson correlation for all numeric columns.",
    )
    parser.add_argument(
        "--correlation-json",
        action="store_true",
        default=False,
        help="Output correlation matrix as JSON.",
    )
    parser.add_argument(
        "--correlation-precision",
        type=int,
        default=4,
        metavar="N",
        help="Decimal places for correlation values (default: 4).",
    )


def correlation_as_dict(result: CorrelationResult) -> Dict[str, Any]:
    pairs: Dict[str, float] = {}
    for (col_a, col_b), val in result.matrix.items():
        pairs[f"{col_a}:{col_b}"] = val
    return {"columns": result.columns, "pairs": pairs}


def maybe_print_correlation(
    args: argparse.Namespace,
    rows: List[Dict[str, str]],
) -> Optional[CorrelationResult]:
    columns: Optional[List[str]] = None
    if getattr(args, "correlate", None):
        columns = args.correlate
    elif getattr(args, "correlate_all", False):
        columns = None  # compute_correlation will use all columns
    else:
        return None

    result = compute_correlation(rows, columns=columns)
    precision = getattr(args, "correlation_precision", 4)

    if getattr(args, "correlation_json", False):
        print(json.dumps(correlation_as_dict(result), indent=2))
    else:
        print(format_correlation(result, precision=precision))

    return result
