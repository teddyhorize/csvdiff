"""Pivot table generation from diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult


class PivotTableError(Exception):
    """Raised when pivot table generation fails."""


@dataclass
class PivotCell:
    added: int = 0
    removed: int = 0
    modified: int = 0

    @property
    def total(self) -> int:
        return self.added + self.removed + self.modified


@dataclass
class PivotTable:
    row_field: str
    col_field: str
    cells: Dict[str, Dict[str, PivotCell]] = field(default_factory=dict)
    row_keys: List[str] = field(default_factory=list)
    col_keys: List[str] = field(default_factory=list)


def _get(row: dict, key: str) -> Optional[str]:
    return row.get(key)


def build_pivot_table(
    result: DiffResult,
    row_field: str,
    col_field: str,
) -> PivotTable:
    """Build a pivot table grouping diff changes by two fields."""
    all_rows = (
        [(r, "added") for r in result.added_rows]
        + [(r, "removed") for r in result.removed_rows]
        + [(r["old"], "modified") for r in result.modified_rows]
    )

    if not all_rows:
        return PivotTable(row_field=row_field, col_field=col_field)

    sample = all_rows[0][0]
    if row_field not in sample:
        raise PivotTableError(f"Row field '{row_field}' not found in data")
    if col_field not in sample:
        raise PivotTableError(f"Column field '{col_field}' not found in data")

    cells: Dict[str, Dict[str, PivotCell]] = {}
    row_keys_seen: List[str] = []
    col_keys_seen: List[str] = []

    for row, change_type in all_rows:
        rk = _get(row, row_field) or "(blank)"
        ck = _get(row, col_field) or "(blank)"

        if rk not in cells:
            cells[rk] = {}
            row_keys_seen.append(rk)
        if ck not in cells[rk]:
            cells[rk][ck] = PivotCell()
        if ck not in col_keys_seen:
            col_keys_seen.append(ck)

        cell = cells[rk][ck]
        if change_type == "added":
            cell.added += 1
        elif change_type == "removed":
            cell.removed += 1
        else:
            cell.modified += 1

    return PivotTable(
        row_field=row_field,
        col_field=col_field,
        cells=cells,
        row_keys=sorted(row_keys_seen),
        col_keys=sorted(col_keys_seen),
    )


def format_pivot_table(table: PivotTable, show_total: bool = True) -> str:
    """Render a PivotTable as a plain-text grid."""
    if not table.row_keys:
        return "(no changes to pivot)"

    col_w = 12
    label_w = max(len(table.row_field), max(len(k) for k in table.row_keys)) + 2

    header = f"{table.row_field:<{label_w}}" + "".join(
        f"{ck:>{col_w}}" for ck in table.col_keys
    )
    if show_total:
        header += f"{'TOTAL':>{col_w}}"
    lines = [header, "-" * len(header)]

    for rk in table.row_keys:
        row_total = 0
        line = f"{rk:<{label_w}}"
        for ck in table.col_keys:
            cell = table.cells.get(rk, {}).get(ck, PivotCell())
            line += f"{cell.total:>{col_w}}"
            row_total += cell.total
        if show_total:
            line += f"{row_total:>{col_w}}"
        lines.append(line)

    return "\n".join(lines)
