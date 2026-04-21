"""CLI helpers for lineage tracking output."""
from __future__ import annotations
import argparse
import json
from typing import Optional
from csvdiff.lineage import Lineage, format_lineage


def register_lineage_args(parser: argparse.ArgumentParser) -> None:
    """Add lineage-related flags to an argument parser."""
    group = parser.add_argument_group("lineage")
    group.add_argument(
        "--lineage",
        action="store_true",
        default=False,
        help="Print transformation lineage after processing.",
    )
    group.add_argument(
        "--lineage-json",
        action="store_true",
        default=False,
        help="Output lineage as JSON instead of plain text.",
    )


def lineage_as_dict(lineage: Lineage) -> dict:
    """Serialize a Lineage object to a plain dict."""
    return {
        "source_file": lineage.source_file,
        "events": [
            {
                "step": ev.step,
                "description": ev.description,
                "affected_columns": ev.affected_columns,
                "affected_rows": ev.affected_rows,
            }
            for ev in lineage.events
        ],
    }


def maybe_print_lineage(
    args: argparse.Namespace,
    lineage: Optional[Lineage],
) -> None:
    """Print lineage if the --lineage flag is set."""
    if lineage is None:
        return
    if getattr(args, "lineage_json", False):
        print(json.dumps(lineage_as_dict(lineage), indent=2))
    elif getattr(args, "lineage", False):
        print(format_lineage(lineage))
