"""Frequency analysis: count value occurrences per column across diff rows."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from csvdiff.differ import DiffResult


class FrequencyError(Exception):
    """Raised when frequency analysis cannot be completed."""


@dataclass
class ColumnFrequency:
    column: str
    counts: Dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    @property
    def unique(self) -> int:
        return len(self.counts)

    def top(self, n: int = 5) -> List[tuple]:
        """Return the top-n (value, count) pairs sorted by count descending."""
        return Counter(self.counts).most_common(n)


@dataclass
class FrequencyResult:
    columns: List[ColumnFrequency] = field(default_factory=list)

    def get(self, column: str) -> ColumnFrequency | None:
        for cf in self.columns:
            if cf.column == column:
                return cf
        return None


def _collect_rows(result: DiffResult, include_unchanged: bool) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    rows.extend(result.added)
    rows.extend(result.removed)
    rows.extend(r.get("new", r) for r in result.modified)
    if include_unchanged:
        rows.extend(result.unchanged)
    return rows


def compute_frequency(
    result: DiffResult,
    columns: List[str] | None = None,
    include_unchanged: bool = False,
) -> FrequencyResult:
    """Compute value frequency for each column across diff rows."""
    rows = _collect_rows(result, include_unchanged)
    if not rows:
        return FrequencyResult()

    all_columns = columns if columns else list(rows[0].keys())
    unknown = [c for c in all_columns if c not in rows[0]]
    if unknown:
        raise FrequencyError(f"Unknown columns: {', '.join(unknown)}")

    freq_map: Dict[str, Counter] = {col: Counter() for col in all_columns}
    for row in rows:
        for col in all_columns:
            val = row.get(col, "")
            freq_map[col][val] += 1

    return FrequencyResult(
        columns=[
            ColumnFrequency(column=col, counts=dict(freq_map[col]))
            for col in all_columns
        ]
    )


def format_frequency(freq: FrequencyResult, top_n: int = 5) -> str:
    if not freq.columns:
        return "No frequency data available."
    lines = []
    for cf in freq.columns:
        lines.append(f"Column: {cf.column}  (total={cf.total}, unique={cf.unique})")
        for val, cnt in cf.top(top_n):
            display = repr(val) if val == "" else val
            lines.append(f"  {display}: {cnt}")
    return "\n".join(lines)
