"""Outlier detection for numeric columns in CSV diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import statistics


class OutlierError(Exception):
    """Raised when outlier detection fails."""


@dataclass
class OutlierResult:
    column: str
    mean: float
    stdev: float
    threshold: float
    outliers: List[Dict[str, str]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.outliers)


def _parse_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def detect_outliers(
    rows: List[Dict[str, str]],
    column: str,
    z_threshold: float = 2.5,
) -> OutlierResult:
    """Detect outliers in *column* using Z-score method."""
    if not rows:
        raise OutlierError("No rows provided for outlier detection.")
    if column not in rows[0]:
        raise OutlierError(f"Column '{column}' not found in rows.")

    values = [(_parse_float(r[column]), r) for r in rows]
    numeric = [(v, r) for v, r in values if v is not None]

    if len(numeric) < 2:
        raise OutlierError(
            f"Column '{column}' has fewer than 2 numeric values."
        )

    nums = [v for v, _ in numeric]
    mean = statistics.mean(nums)
    stdev = statistics.pstdev(nums)

    if stdev == 0.0:
        return OutlierResult(
            column=column, mean=mean, stdev=0.0,
            threshold=z_threshold, outliers=[]
        )

    outliers = [
        r for v, r in numeric
        if abs((v - mean) / stdev) > z_threshold
    ]
    return OutlierResult(
        column=column, mean=mean, stdev=stdev,
        threshold=z_threshold, outliers=outliers,
    )


def format_outlier(result: OutlierResult, *, color: bool = False) -> str:
    lines = [
        f"Outliers in '{result.column}': {result.count} found",
        f"  mean={result.mean:.4f}  stdev={result.stdev:.4f}  "
        f"z_threshold={result.threshold}",
    ]
    for row in result.outliers:
        val = row.get(result.column, "?")
        label = "  row: " + ", ".join(f"{k}={v}" for k, v in row.items())
        if color:
            label = f"\033[33m{label}\033[0m"
        lines.append(label)
    return "\n".join(lines)
