"""Compute pairwise column correlations from CSV row data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


class CorrelationError(Exception):
    """Raised when correlation computation fails."""


@dataclass
class CorrelationResult:
    columns: List[str]
    matrix: Dict[Tuple[str, str], Optional[float]] = field(default_factory=dict)

    def get(self, col_a: str, col_b: str) -> Optional[float]:
        key = (col_a, col_b) if (col_a, col_b) in self.matrix else (col_b, col_a)
        return self.matrix.get(key)


def _parse_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _pearson(xs: List[float], ys: List[float]) -> Optional[float]:
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def compute_correlation(
    rows: List[Dict[str, str]],
    columns: Optional[List[str]] = None,
) -> CorrelationResult:
    if not rows:
        raise CorrelationError("Cannot compute correlation on empty rows.")
    all_cols = list(rows[0].keys())
    target = columns if columns else all_cols
    for col in target:
        if col not in all_cols:
            raise CorrelationError(f"Column not found: {col!r}")
    matrix: Dict[Tuple[str, str], Optional[float]] = {}
    for i, col_a in enumerate(target):
        for col_b in target[i:]:
            pairs = [
                (_parse_float(r[col_a]), _parse_float(r[col_b]))
                for r in rows
            ]
            valid = [(x, y) for x, y in pairs if x is not None and y is not None]
            xs, ys = zip(*valid) if valid else ([], [])
            matrix[(col_a, col_b)] = _pearson(list(xs), list(ys))
    return CorrelationResult(columns=target, matrix=matrix)


def format_correlation(result: CorrelationResult, precision: int = 4) -> str:
    cols = result.columns
    col_w = max(len(c) for c in cols) if cols else 8
    header = " " * (col_w + 2) + "  ".join(c.ljust(col_w) for c in cols)
    lines = [header]
    for row_col in cols:
        row_vals = []
        for col in cols:
            val = result.get(row_col, col)
            row_vals.append(f"{val:.{precision}f}" if val is not None else "  N/A  ")
        lines.append(row_col.ljust(col_w) + "  " + "  ".join(v.ljust(col_w) for v in row_vals))
    return "\n".join(lines)
