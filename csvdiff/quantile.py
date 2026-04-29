"""Quantile computation for numeric columns in CSV diff results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class QuantileError(Exception):
    """Raised when quantile computation fails."""


@dataclass
class ColumnQuantiles:
    column: str
    count: int
    min: Optional[float]
    q1: Optional[float]
    median: Optional[float]
    q3: Optional[float]
    max: Optional[float]

    def iqr(self) -> Optional[float]:
        if self.q1 is None or self.q3 is None:
            return None
        return self.q3 - self.q1


@dataclass
class QuantileResult:
    columns: Dict[str, ColumnQuantiles] = field(default_factory=dict)

    def get(self, column: str) -> Optional[ColumnQuantiles]:
        return self.columns.get(column)


def _parse_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _percentile(sorted_values: List[float], pct: float) -> float:
    """Return the percentile value using linear interpolation."""
    n = len(sorted_values)
    if n == 1:
        return sorted_values[0]
    idx = pct / 100.0 * (n - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= n:
        return sorted_values[-1]
    frac = idx - lo
    return sorted_values[lo] + frac * (sorted_values[hi] - sorted_values[lo])


def compute_quantiles(
    rows: List[Dict[str, str]],
    columns: Optional[List[str]] = None,
) -> QuantileResult:
    """Compute quantile statistics for numeric columns in *rows*."""
    if not rows:
        return QuantileResult()

    all_columns = list(rows[0].keys())
    target = columns if columns is not None else all_columns

    for col in target:
        if col not in all_columns:
            raise QuantileError(f"Column not found: {col!r}")

    result = QuantileResult()
    for col in target:
        values = [v for r in rows if (v := _parse_float(r.get(col, ""))) is not None]
        if not values:
            result.columns[col] = ColumnQuantiles(
                column=col, count=0,
                min=None, q1=None, median=None, q3=None, max=None,
            )
            continue
        sv = sorted(values)
        result.columns[col] = ColumnQuantiles(
            column=col,
            count=len(sv),
            min=sv[0],
            q1=_percentile(sv, 25),
            median=_percentile(sv, 50),
            q3=_percentile(sv, 75),
            max=sv[-1],
        )
    return result


def format_quantiles(result: QuantileResult) -> str:
    """Return a human-readable summary of quantile results."""
    if not result.columns:
        return "No quantile data."
    lines = []
    for col, q in result.columns.items():
        if q.count == 0:
            lines.append(f"{col}: no numeric data")
        else:
            lines.append(
                f"{col}: min={q.min} Q1={q.q1} median={q.median} "
                f"Q3={q.q3} max={q.max} IQR={q.iqr()}"
            )
    return "\n".join(lines)
