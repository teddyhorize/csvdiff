"""CLI helpers for outlier detection."""
from __future__ import annotations

import argparse
import json
from typing import Dict, List, Optional

from csvdiff.outlier import OutlierResult, detect_outliers, format_outlier


def register_outlier_args(parser: argparse.ArgumentParser) -> None:
    """Add outlier-related flags to *parser*."""
    parser.add_argument(
        "--outlier-column",
        metavar="COL",
        default=None,
        help="Column to check for numeric outliers.",
    )
    parser.add_argument(
        "--outlier-z",
        type=float,
        default=2.5,
        metavar="Z",
        help="Z-score threshold for outlier detection (default: 2.5).",
    )
    parser.add_argument(
        "--outlier-json",
        action="store_true",
        default=False,
        help="Output outlier results as JSON.",
    )


def outlier_as_dict(result: OutlierResult) -> Dict:
    return {
        "column": result.column,
        "mean": result.mean,
        "stdev": result.stdev,
        "threshold": result.threshold,
        "outlier_count": result.count,
        "outliers": result.outliers,
    }


def maybe_print_outliers(
    args: argparse.Namespace,
    rows: List[Dict[str, str]],
    *,
    color: bool = False,
) -> Optional[OutlierResult]:
    """Run outlier detection and print if --outlier-column is set."""
    column: Optional[str] = getattr(args, "outlier_column", None)
    if not column:
        return None

    z: float = getattr(args, "outlier_z", 2.5)
    as_json: bool = getattr(args, "outlier_json", False)

    result = detect_outliers(rows, column=column, z_threshold=z)

    if as_json:
        print(json.dumps(outlier_as_dict(result), indent=2))
    else:
        print(format_outlier(result, color=color))

    return result
