"""Pivot diff results for column-centric comparison views."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from csvdiff.differ import DiffResult


@dataclass
class ColumnPivot:
    column: str
    added_values: List[str] = field(default_factory=list)
    removed_values: List[str] = field(default_factory=list)
    modified_values: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.added_values) + len(self.removed_values) + len(self.modified_values)


def pivot_by_column(result: DiffResult) -> Dict[str, ColumnPivot]:
    """Reorganise a DiffResult so changes are grouped by column name."""
    pivots: Dict[str, ColumnPivot] = {}

    def _get(col: str) -> ColumnPivot:
        if col not in pivots:
            pivots[col] = ColumnPivot(column=col)
        return pivots[col]

    for row in result.get("added", []):
        for col, val in row.items():
            _get(col).added_values.append(str(val))

    for row in result.get("removed", []):
        for col, val in row.items():
            _get(col).removed_values.append(str(val))

    for change in result.get("modified", []):
        old = change.get("old", {})
        new = change.get("new", {})
        all_cols = set(old) | set(new)
        for col in all_cols:
            ov, nv = str(old.get(col, "")), str(new.get(col, ""))
            if ov != nv:
                _get(col).modified_values.append((ov, nv))

    return pivots


def format_pivot(pivots: Dict[str, ColumnPivot], color: bool = True) -> str:
    """Render pivot data as a human-readable string."""
    if not pivots:
        return "No column-level changes detected."

    lines: List[str] = []
    for col, pivot in sorted(pivots.items(), key=lambda x: -x[1].total_changes):
        header = f"[{col}]  {pivot.total_changes} change(s)"
        lines.append(header)
        for v in pivot.added_values:
            prefix = "  + " if not color else "\033[32m  + \033[0m"
            lines.append(f"{prefix}{v}")
        for v in pivot.removed_values:
            prefix = "  - " if not color else "\033[31m  - \033[0m"
            lines.append(f"{prefix}{v}")
        for ov, nv in pivot.modified_values:
            prefix = "  ~ " if not color else "\033[33m  ~ \033[0m"
            lines.append(f"{prefix}{ov!r} -> {nv!r}")
    return "\n".join(lines)
