"""Threshold-based diff filtering: suppress output when changes are below a threshold."""
from dataclasses import dataclass
from typing import Optional
from csvdiff.differ import DiffResult


class ThresholdError(Exception):
    pass


@dataclass
class ThresholdOptions:
    max_added: Optional[int] = None
    max_removed: Optional[int] = None
    max_modified: Optional[int] = None
    max_total: Optional[int] = None
    max_added_pct: Optional[float] = None
    max_removed_pct: Optional[float] = None


def _total_rows(result: DiffResult) -> int:
    return len(result.added) + len(result.removed) + len(result.modified)


def check_threshold(result: DiffResult, options: ThresholdOptions, total_rows: int = 0) -> bool:
    """Return True if result is within all thresholds, False if any threshold is exceeded."""
    if options.max_added is not None and len(result.added) > options.max_added:
        return False
    if options.max_removed is not None and len(result.removed) > options.max_removed:
        return False
    if options.max_modified is not None and len(result.modified) > options.max_modified:
        return False
    total = _total_rows(result)
    if options.max_total is not None and total > options.max_total:
        return False
    if total_rows > 0:
        if options.max_added_pct is not None:
            if len(result.added) / total_rows * 100 > options.max_added_pct:
                return False
        if options.max_removed_pct is not None:
            if len(result.removed) / total_rows * 100 > options.max_removed_pct:
                return False
    return True


def format_threshold_warning(result: DiffResult, options: ThresholdOptions, total_rows: int = 0) -> str:
    lines = ["Diff exceeds threshold limits:"]
    if options.max_added is not None and len(result.added) > options.max_added:
        lines.append(f"  added rows: {len(result.added)} > {options.max_added}")
    if options.max_removed is not None and len(result.removed) > options.max_removed:
        lines.append(f"  removed rows: {len(result.removed)} > {options.max_removed}")
    if options.max_modified is not None and len(result.modified) > options.max_modified:
        lines.append(f"  modified rows: {len(result.modified)} > {options.max_modified}")
    total = _total_rows(result)
    if options.max_total is not None and total > options.max_total:
        lines.append(f"  total changes: {total} > {options.max_total}")
    if total_rows > 0:
        if options.max_added_pct is not None:
            pct = len(result.added) / total_rows * 100
            if pct > options.max_added_pct:
                lines.append(f"  added %: {pct:.1f}% > {options.max_added_pct}%")
        if options.max_removed_pct is not None:
            pct = len(result.removed) / total_rows * 100
            if pct > options.max_removed_pct:
                lines.append(f"  removed %: {pct:.1f}% > {options.max_removed_pct}%")
    return "\n".join(lines)
