"""CLI helpers for the drift detection feature."""
from __future__ import annotations

import argparse
import json
from typing import Optional

from csvdiff.drift import DriftReport, format_drift


def register_drift_args(parser: argparse.ArgumentParser) -> None:
    """Add drift-related arguments to *parser*."""
    group = parser.add_argument_group("drift")
    group.add_argument(
        "--drift",
        action="store_true",
        default=False,
        help="Show a drift report comparing the two CSV files.",
    )
    group.add_argument(
        "--drift-label",
        metavar="LABEL",
        default="",
        help="Optional label to prefix the drift report output.",
    )
    group.add_argument(
        "--drift-json",
        action="store_true",
        default=False,
        help="Output drift report as JSON instead of plain text.",
    )


def drift_as_dict(report: DriftReport) -> dict:
    """Serialise a DriftReport to a plain dictionary."""
    return {
        "has_drift": report.has_drift,
        "label": report.label,
        "added_rows": report.added_rows,
        "removed_rows": report.removed_rows,
        "modified_rows": report.modified_rows,
        "changed_columns": report.changed_columns,
        "schema_drift": {
            "added_columns": list(report.schema_drift.added_columns),
            "removed_columns": list(report.schema_drift.removed_columns),
            "reordered": report.schema_drift.reordered,
        },
    }


def maybe_print_drift(
    args: argparse.Namespace,
    report: Optional[DriftReport],
    color: bool = False,
) -> None:
    """Print the drift report if the ``--drift`` flag is set."""
    if not getattr(args, "drift", False) or report is None:
        return
    if getattr(args, "drift_json", False):
        print(json.dumps(drift_as_dict(report), indent=2))
    else:
        print(format_drift(report, color=color))
