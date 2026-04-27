"""Compute and format data density metrics for CSV diff results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from csvdiff.differ import DiffResult


class DensityError(Exception):
    """Raised when density computation fails."""


@dataclass
class ColumnDensity:
    column: str
    total_cells: int
    non_empty_cells: int

    @property
    def density(self) -> float:
        if self.total_cells == 0:
            return 0.0
        return self.non_empty_cells / self.total_cells

    @property
    def empty_cells(self) -> int:
        return self.total_cells - self.non_empty_cells


@dataclass
class DensityResult:
    columns: List[ColumnDensity]
    total_rows: int

    def by_column(self, name: str) -> ColumnDensity:
        for col in self.columns:
            if col.column == name:
                return col
        raise DensityError(f"Column not found: {name!r}")


def _count_non_empty(rows: List[Dict[str, str]], column: str) -> int:
    return sum(1 for row in rows if row.get(column, "").strip() != "")


def compute_density(rows: List[Dict[str, str]]) -> DensityResult:
    """Compute per-column density for a list of rows."""
    if not rows:
        return DensityResult(columns=[], total_rows=0)

    headers = list(rows[0].keys())
    total = len(rows)
    columns = [
        ColumnDensity(
            column=col,
            total_cells=total,
            non_empty_cells=_count_non_empty(rows, col),
        )
        for col in headers
    ]
    return DensityResult(columns=columns, total_rows=total)


def density_from_diff(result: DiffResult) -> Dict[str, DensityResult]:
    """Compute density for left and right sides of a diff."""
    all_rows_left = (
        list(result.removed)
        + [old for old, _ in result.modified]
    )
    all_rows_right = (
        list(result.added)
        + [new for _, new in result.modified]
    )
    return {
        "left": compute_density(all_rows_left),
        "right": compute_density(all_rows_right),
    }


def format_density(result: DensityResult) -> str:
    """Return a human-readable density report."""
    if not result.columns:
        return "No data."
    lines = [f"Rows: {result.total_rows}"]
    for col in result.columns:
        pct = col.density * 100
        lines.append(
            f"  {col.column}: {pct:.1f}% filled "
            f"({col.non_empty_cells}/{col.total_cells})"
        )
    return "\n".join(lines)
