"""Column reordering for CSV diff rows."""

from dataclasses import dataclass, field
from typing import List, Dict, Any


class ReorderError(Exception):
    """Raised when column reordering fails."""


@dataclass
class ReorderOptions:
    columns: List[str] = field(default_factory=list)
    move_to_front: List[str] = field(default_factory=list)
    move_to_back: List[str] = field(default_factory=list)


def _validate(options: ReorderOptions, headers: List[str]) -> None:
    if options.columns:
        missing = [c for c in options.columns if c not in headers]
        if missing:
            raise ReorderError(f"Unknown columns: {missing}")
    for col in options.move_to_front + options.move_to_back:
        if col not in headers:
            raise ReorderError(f"Unknown column: {col!r}")


def reorder_headers(headers: List[str], options: ReorderOptions) -> List[str]:
    """Return a new header list according to reorder options."""
    _validate(options, headers)

    if options.columns:
        remaining = [h for h in headers if h not in options.columns]
        return options.columns + remaining

    result = list(headers)
    for col in reversed(options.move_to_front):
        result.remove(col)
        result.insert(0, col)
    for col in options.move_to_back:
        result.remove(col)
        result.append(col)
    return result


def reorder_row(row: Dict[str, Any], ordered_headers: List[str]) -> Dict[str, Any]:
    """Return a new dict with keys in the given order."""
    return {k: row[k] for k in ordered_headers if k in row}


def reorder_rows(
    rows: List[Dict[str, Any]],
    headers: List[str],
    options: ReorderOptions,
) -> tuple:
    """Return (new_headers, reordered_rows)."""
    new_headers = reorder_headers(headers, options)
    new_rows = [reorder_row(r, new_headers) for r in rows]
    return new_headers, new_rows
