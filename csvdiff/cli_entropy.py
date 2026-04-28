"""CLI helpers for the entropy feature."""
from __future__ import annotations

import argparse
import json
from typing import Dict, List, Optional

from csvdiff.entropy import ColumnEntropy, EntropyResult, compute_entropy, format_entropy


def register_entropy_args(parser: argparse.ArgumentParser) -> None:
    """Attach entropy-related arguments to *parser*."""
    parser.add_argument(
        "--entropy",
        action="store_true",
        default=False,
        help="Compute Shannon entropy for each column.",
    )
    parser.add_argument(
        "--entropy-columns",
        nargs="+",
        metavar="COL",
        default=None,
        help="Limit entropy computation to these columns.",
    )
    parser.add_argument(
        "--entropy-json",
        action="store_true",
        default=False,
        help="Output entropy results as JSON.",
    )
    parser.add_argument(
        "--entropy-threshold",
        type=float,
        default=None,
        metavar="THRESHOLD",
        help="Warn when normalized entropy falls below this value.",
    )


def entropy_as_dict(result: EntropyResult) -> List[Dict]:
    """Serialize an EntropyResult to a list of dicts suitable for JSON output."""
    return [
        {
            "column": col.column,
            "entropy": col.entropy,
            "normalized": col.normalized,
            "unique_values": col.unique_values,
            "total_values": col.total_values,
            "max_entropy": col.max_entropy,
        }
        for col in result.columns
    ]


def maybe_print_entropy(
    args: argparse.Namespace,
    rows: List[Dict[str, str]],
) -> Optional[EntropyResult]:
    """Compute and print entropy if --entropy flag is set; return result or None."""
    if not getattr(args, "entropy", False):
        return None

    columns = getattr(args, "entropy_columns", None)
    result = compute_entropy(rows, columns=columns)

    threshold = getattr(args, "entropy_threshold", None)
    if threshold is not None:
        for col in result.columns:
            norm = col.normalized
            if norm is not None and norm < threshold:
                print(
                    f"[WARN] Low entropy in column '{col.column}': "
                    f"normalized={norm:.4f} < threshold={threshold}"
                )

    if getattr(args, "entropy_json", False):
        print(json.dumps(entropy_as_dict(result), indent=2))
    else:
        print(format_entropy(result))

    return result
