"""CLI helpers for the pivot-table feature."""
from __future__ import annotations

import argparse
import json
from typing import Optional

from csvdiff.differ import DiffResult
from csvdiff.pivot_table import (
    PivotTable,
    PivotTableError,
    build_pivot_table,
    format_pivot_table,
)


def register_pivot_table_args(parser: argparse.ArgumentParser) -> None:
    """Add pivot-table arguments to an existing argument parser."""
    grp = parser.add_argument_group("pivot table")
    grp.add_argument(
        "--pivot-row",
        metavar="FIELD",
        default=None,
        help="Field to use as pivot table row dimension.",
    )
    grp.add_argument(
        "--pivot-col",
        metavar="FIELD",
        default=None,
        help="Field to use as pivot table column dimension.",
    )
    grp.add_argument(
        "--pivot-json",
        action="store_true",
        default=False,
        help="Output pivot table as JSON instead of plain text.",
    )


def pivot_table_as_dict(table: PivotTable) -> dict:
    """Serialise a PivotTable to a JSON-safe dict."""
    return {
        "row_field": table.row_field,
        "col_field": table.col_field,
        "row_keys": table.row_keys,
        "col_keys": table.col_keys,
        "cells": {
            rk: {
                ck: {
                    "added": cell.added,
                    "removed": cell.removed,
                    "modified": cell.modified,
                    "total": cell.total,
                }
                for ck, cell in cols.items()
            }
            for rk, cols in table.cells.items()
        },
    }


def maybe_print_pivot_table(
    args: argparse.Namespace,
    result: DiffResult,
    use_color: bool = False,
) -> Optional[PivotTable]:
    """If --pivot-row and --pivot-col are set, build and print the pivot table."""
    row_field: Optional[str] = getattr(args, "pivot_row", None)
    col_field: Optional[str] = getattr(args, "pivot_col", None)

    if not row_field or not col_field:
        return None

    try:
        table = build_pivot_table(result, row_field, col_field)
    except PivotTableError as exc:
        print(f"[pivot-table error] {exc}")
        return None

    if getattr(args, "pivot_json", False):
        print(json.dumps(pivot_table_as_dict(table), indent=2))
    else:
        print()
        print(f"Pivot table  ({row_field} × {col_field})")
        print(format_pivot_table(table))

    return table
