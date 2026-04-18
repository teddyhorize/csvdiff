"""Detect and report duplicate rows within a CSV dataset."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DedupeError(Exception):
    pass


@dataclass
class DedupeResult:
    duplicate_groups: Dict[str, List[dict]] = field(default_factory=dict)
    total_duplicates: int = 0
    checked_columns: List[str] = field(default_factory=list)


def _row_key(row: dict, columns: List[str]) -> str:
    return "|".join(str(row.get(c, "")) for c in columns)


def find_duplicates(
    rows: List[dict],
    columns: Optional[List[str]] = None,
) -> DedupeResult:
    if not rows:
        return DedupeResult()

    all_cols = list(rows[0].keys())
    key_cols = columns if columns else all_cols

    missing = [c for c in key_cols if c not in all_cols]
    if missing:
        raise DedupeError(f"Columns not found: {missing}")

    seen: Dict[str, List[dict]] = {}
    for row in rows:
        k = _row_key(row, key_cols)
        seen.setdefault(k, []).append(row)

    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    total = sum(len(v) - 1 for v in dupes.values())

    return DedupeResult(
        duplicate_groups=dupes,
        total_duplicates=total,
        checked_columns=key_cols,
    )


def format_dedupe(result: DedupeResult, color: bool = False) -> str:
    if result.total_duplicates == 0:
        return "No duplicate rows found."

    lines = [f"Found {result.total_duplicates} duplicate row(s):\n"]
    for key, group in result.duplicate_groups.items():
        label = f"  Key({key}) — {len(group)} occurrences"
        if color:
            label = f"\033[33m{label}\033[0m"
        lines.append(label)
    return "\n".join(lines)
