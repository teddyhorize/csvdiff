"""Flatten nested/repeated column values into separate rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


class FlattenError(Exception):
    """Raised when flattening fails."""


@dataclass
class FlattenOptions:
    column: str
    separator: str = "|"
    strip: bool = True
    keep_empty: bool = False


@dataclass
class FlattenResult:
    original_count: int
    expanded_count: int
    rows: List[Dict[str, str]] = field(default_factory=list)


def _split_cell(value: str, separator: str, strip: bool) -> List[str]:
    parts = value.split(separator)
    if strip:
        parts = [p.strip() for p in parts]
    return parts


def flatten_rows(
    rows: List[Dict[str, str]],
    options: FlattenOptions,
) -> FlattenResult:
    """Expand rows by splitting a multi-value column into individual rows."""
    if not rows:
        return FlattenResult(original_count=0, expanded_count=0, rows=[])

    col = options.column
    if col not in rows[0]:
        raise FlattenError(f"Column '{col}' not found in rows.")

    expanded: List[Dict[str, str]] = []
    for row in rows:
        cell = row.get(col, "")
        parts = _split_cell(cell, options.separator, options.strip)
        for part in parts:
            if not part and not options.keep_empty:
                continue
            new_row = dict(row)
            new_row[col] = part
            expanded.append(new_row)

    return FlattenResult(
        original_count=len(rows),
        expanded_count=len(expanded),
        rows=expanded,
    )


def format_flatten(result: FlattenResult) -> str:
    """Return a human-readable summary of the flatten operation."""
    return (
        f"Flattened {result.original_count} row(s) "
        f"into {result.expanded_count} row(s)."
    )
