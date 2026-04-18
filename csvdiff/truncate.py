"""Truncation utilities for limiting output length in diffs."""

from dataclasses import dataclass
from typing import List, Dict, Any


class TruncateError(Exception):
    pass


@dataclass
class TruncateOptions:
    max_rows: int = 0        # 0 = no limit
    max_cols: int = 0        # 0 = no limit
    max_cell_len: int = 0    # 0 = no limit


def truncate_cell(value: str, max_len: int) -> str:
    if max_len <= 0 or len(value) <= max_len:
        return value
    return value[:max_len] + "..."


def truncate_rows(rows: List[Dict[str, Any]], max_rows: int) -> List[Dict[str, Any]]:
    if max_rows <= 0:
        return rows
    return rows[:max_rows]


def truncate_columns(rows: List[Dict[str, Any]], columns: List[str], max_cols: int) -> List[Dict[str, Any]]:
    if max_cols <= 0 or not rows:
        return rows
    limited = columns[:max_cols]
    return [{k: v for k, v in row.items() if k in limited} for row in rows]


def apply_truncation(
    rows: List[Dict[str, Any]],
    columns: List[str],
    options: TruncateOptions,
) -> List[Dict[str, Any]]:
    if options.max_rows < 0 or options.max_cols < 0 or options.max_cell_len < 0:
        raise TruncateError("TruncateOptions values must be non-negative.")
    rows = truncate_rows(rows, options.max_rows)
    rows = truncate_columns(rows, columns, options.max_cols)
    if options.max_cell_len > 0:
        rows = [
            {k: truncate_cell(str(v), options.max_cell_len) for k, v in row.items()}
            for row in rows
        ]
    return rows
