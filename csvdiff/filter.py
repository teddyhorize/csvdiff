"""Filtering utilities for restricting diff scope to specific columns or rows."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class FilterOptions:
    columns: List[str] = field(default_factory=list)
    exclude_columns: List[str] = field(default_factory=list)
    row_limit: Optional[int] = None


class FilterError(Exception):
    pass


def filter_columns(rows: List[Dict[str, Any]], options: FilterOptions) -> List[Dict[str, Any]]:
    """Return rows with only the selected columns (or minus excluded ones)."""
    if not rows:
        return rows

    available = set(rows[0].keys())

    if options.columns:
        unknown = set(options.columns) - available
        if unknown:
            raise FilterError(f"Unknown columns: {', '.join(sorted(unknown))}")
        keep = options.columns
    else:
        keep = [c for c in rows[0].keys() if c not in options.exclude_columns]

    return [{k: row[k] for k in keep if k in row} for row in rows]


def filter_rows(rows: List[Dict[str, Any]], options: FilterOptions) -> List[Dict[str, Any]]:
    """Apply row limit if specified."""
    if options.row_limit is not None:
        return rows[: options.row_limit]
    return rows


def apply_filters(
    rows: List[Dict[str, Any]], options: FilterOptions
) -> List[Dict[str, Any]]:
    """Apply all filters in order."""
    rows = filter_rows(rows, options)
    rows = filter_columns(rows, options)
    return rows
