"""Z-score normalization for numeric columns in CSV rows."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ZScoreError(Exception):
    """Raised when z-score normalization fails."""


@dataclass
class ZScoreColumn:
    name: str
    mean: float
    stdev: float
    count: int

    def normalize(self, value: float) -> Optional[float]:
        """Return z-score for a value, or None if stdev is zero."""
        if self.stdev == 0.0:
            return None
        return (value - self.mean) / self.stdev


@dataclass
class ZScoreResult:
    columns: Dict[str, ZScoreColumn] = field(default_factory=dict)

    def get(self, column: str) -> Optional[ZScoreColumn]:
        return self.columns.get(column)


def _parse_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def compute_zscore(rows: List[Dict[str, str]], columns: Optional[List[str]] = None) -> ZScoreResult:
    """Compute z-score statistics for numeric columns."""
    if not rows:
        return ZScoreResult()

    available = list(rows[0].keys())
    targets = columns if columns else available

    result = ZScoreResult()
    for col in targets:
        if col not in available:
            raise ZScoreError(f"Column not found: {col!r}")
        values = [v for r in rows if (v := _parse_float(r.get(col, ""))) is not None]
        if not values:
            continue
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        stdev = math.sqrt(variance)
        result.columns[col] = ZScoreColumn(name=col, mean=mean, stdev=stdev, count=n)

    return result


def normalize_rows(
    rows: List[Dict[str, str]],
    zscore: ZScoreResult,
    suffix: str = "_z",
) -> List[Dict[str, str]]:
    """Return rows with z-score columns appended."""
    out = []
    for row in rows:
        new_row = dict(row)
        for col, stats in zscore.columns.items():
            raw = _parse_float(row.get(col, ""))
            if raw is not None:
                z = stats.normalize(raw)
                new_row[col + suffix] = "" if z is None else f"{z:.6f}"
            else:
                new_row[col + suffix] = ""
        out.append(new_row)
    return out
