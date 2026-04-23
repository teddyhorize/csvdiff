"""Aggregate numeric columns across diff result rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult


class AggregateError(Exception):
    """Raised when aggregation fails."""


@dataclass
class AggregateOptions:
    columns: List[str] = field(default_factory=list)
    include_added: bool = True
    include_removed: bool = True
    include_modified: bool = True


@dataclass
class AggregateResult:
    column: str
    count: int
    total: float
    minimum: Optional[float]
    maximum: Optional[float]
    mean: Optional[float]


def _collect_values(rows: List[Dict[str, str]], column: str) -> List[float]:
    values: List[float] = []
    for row in rows:
        raw = row.get(column, "").strip()
        if raw:
            try:
                values.append(float(raw))
            except ValueError:
                pass
    return values


def aggregate_column(
    result: DiffResult,
    column: str,
    opts: Optional[AggregateOptions] = None,
) -> AggregateResult:
    if opts is None:
        opts = AggregateOptions()

    rows: List[Dict[str, str]] = []
    if opts.include_added:
        rows.extend(result.added)
    if opts.include_removed:
        rows.extend(result.removed)
    if opts.include_modified:
        rows.extend(new for _, new in result.modified)

    values = _collect_values(rows, column)
    count = len(values)
    total = sum(values)
    minimum = min(values) if values else None
    maximum = max(values) if values else None
    mean = (total / count) if count else None

    return AggregateResult(
        column=column,
        count=count,
        total=total,
        minimum=minimum,
        maximum=maximum,
        mean=mean,
    )


def aggregate_diff(
    result: DiffResult,
    opts: Optional[AggregateOptions] = None,
) -> List[AggregateResult]:
    if opts is None:
        opts = AggregateOptions()
    if not opts.columns:
        raise AggregateError("No columns specified for aggregation.")
    return [aggregate_column(result, col, opts) for col in opts.columns]


def format_aggregate(results: List[AggregateResult]) -> str:
    if not results:
        return "No aggregation results."
    lines = []
    for r in results:
        lines.append(
            f"{r.column}: count={r.count}, sum={r.total:.4g}, "
            f"min={r.minimum}, max={r.maximum}, mean={r.mean:.4g if r.mean is not None else 'N/A'}"
        )
    return "\n".join(lines)
