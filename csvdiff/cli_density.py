"""CLI helpers for the density feature."""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List, Optional

from csvdiff.density import ColumnDensity, DensityResult, compute_density, format_density


def register_density_args(parser: argparse.ArgumentParser) -> None:
    """Add --density and --density-json flags to an argument parser."""
    parser.add_argument(
        "--density",
        action="store_true",
        default=False,
        help="Print per-column data density for the input rows.",
    )
    parser.add_argument(
        "--density-json",
        action="store_true",
        default=False,
        help="Output density report as JSON.",
    )


def density_as_dict(result: DensityResult) -> Dict[str, Any]:
    """Serialise a DensityResult to a plain dict."""
    return {
        "total_rows": result.total_rows,
        "columns": [
            {
                "column": col.column,
                "total_cells": col.total_cells,
                "non_empty_cells": col.non_empty_cells,
                "empty_cells": col.empty_cells,
                "density": round(col.density, 4),
            }
            for col in result.columns
        ],
    }


def maybe_print_density(
    args: argparse.Namespace,
    rows: List[Dict[str, str]],
) -> Optional[DensityResult]:
    """If --density or --density-json is set, compute and print the report."""
    if not (getattr(args, "density", False) or getattr(args, "density_json", False)):
        return None

    result = compute_density(rows)

    if getattr(args, "density_json", False):
        print(json.dumps(density_as_dict(result), indent=2))
    else:
        print(format_density(result))

    return result
