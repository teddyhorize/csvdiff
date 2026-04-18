"""Support for ignoring specific columns or row patterns during diff."""

from dataclasses import dataclass, field
from typing import List, Optional
import re


class IgnoreError(Exception):
    pass


@dataclass
class IgnoreOptions:
    columns: List[str] = field(default_factory=list)
    row_pattern: Optional[str] = None  # regex applied to entire row as joined string


def _compile_pattern(pattern: str) -> re.Pattern:
    try:
        return re.compile(pattern)
    except re.error as e:
        raise IgnoreError(f"Invalid row pattern '{pattern}': {e}")


def apply_column_ignores(rows: List[dict], columns: List[str]) -> List[dict]:
    """Return rows with specified columns removed."""
    if not columns:
        return rows
    ignore_set = set(columns)
    return [{k: v for k, v in row.items() if k not in ignore_set} for row in rows]


def apply_row_ignores(rows: List[dict], pattern: Optional[str]) -> List[dict]:
    """Return rows that do NOT match the given regex pattern."""
    if not pattern:
        return rows
    compiled = _compile_pattern(pattern)
    result = []
    for row in rows:
        joined = ",".join(str(v) for v in row.values())
        if not compiled.search(joined):
            result.append(row)
    return result


def apply_ignores(rows: List[dict], options: IgnoreOptions) -> List[dict]:
    rows = apply_column_ignores(rows, options.columns)
    rows = apply_row_ignores(rows, options.row_pattern)
    return rows
