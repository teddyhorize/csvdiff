"""Heatmap: visualize change intensity across columns and rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult


class HeatmapError(Exception):
    """Raised when heatmap generation fails."""


@dataclass
class HeatmapCell:
    column: str
    change_count: int
    intensity: float  # 0.0 – 1.0


@dataclass
class Heatmap:
    columns: List[str]
    cells: Dict[str, HeatmapCell] = field(default_factory=dict)
    max_changes: int = 0


def _count_column_changes(result: DiffResult) -> Dict[str, int]:
    """Return a mapping of column -> number of modified values."""
    counts: Dict[str, int] = {}
    for _key, changes in result.modified.items():
        for col in changes:
            counts[col] = counts.get(col, 0) + 1
    return counts


def build_heatmap(result: DiffResult, columns: Optional[List[str]] = None) -> Heatmap:
    """Build a Heatmap from a DiffResult.

    Args:
        result: The diff result to analyse.
        columns: Optional explicit column list.  Defaults to all columns that
                 appear in modified rows.

    Returns:
        A populated Heatmap instance.
    """
    counts = _count_column_changes(result)

    if columns is None:
        columns = sorted(counts.keys())

    if not columns:
        return Heatmap(columns=[], cells={}, max_changes=0)

    max_changes = max((counts.get(c, 0) for c in columns), default=0)

    cells: Dict[str, HeatmapCell] = {}
    for col in columns:
        n = counts.get(col, 0)
        intensity = (n / max_changes) if max_changes > 0 else 0.0
        cells[col] = HeatmapCell(column=col, change_count=n, intensity=intensity)

    return Heatmap(columns=columns, cells=cells, max_changes=max_changes)


def format_heatmap(heatmap: Heatmap, use_color: bool = True) -> str:
    """Render a heatmap as a human-readable table."""
    if not heatmap.columns:
        return "(no column changes detected)"

    # ANSI colour bands: low → high
    _BANDS = [
        (0.0, "\033[0m"),    # reset / no change
        (0.25, "\033[33m"),  # yellow
        (0.5, "\033[93m"),   # bright yellow
        (0.75, "\033[31m"),  # red
        (1.0, "\033[91m"),   # bright red
    ]
    _RESET = "\033[0m"

    def _color(intensity: float) -> str:
        chosen = _BANDS[0][1]
        for threshold, code in _BANDS:
            if intensity >= threshold:
                chosen = code
        return chosen

    col_w = max(len(c) for c in heatmap.columns)
    lines = [f"  {'Column':<{col_w}}  Changes  Intensity"]
    lines.append("  " + "-" * (col_w + 22))
    for col in heatmap.columns:
        cell = heatmap.cells[col]
        bar = int(cell.intensity * 10)
        bar_str = "█" * bar + "░" * (10 - bar)
        if use_color:
            color = _color(cell.intensity)
            line = f"  {col:<{col_w}}  {cell.change_count:>7}  {color}{bar_str}{_RESET}"
        else:
            line = f"  {col:<{col_w}}  {cell.change_count:>7}  {bar_str}"
        lines.append(line)
    return "\n".join(lines)
