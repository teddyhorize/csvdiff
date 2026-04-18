from dataclasses import dataclass, field
from typing import Dict, List
from csvdiff.differ import DiffResult


@dataclass
class DiffStats:
    total_rows_a: int = 0
    total_rows_b: int = 0
    added_rows: int = 0
    removed_rows: int = 0
    modified_rows: int = 0
    added_columns: int = 0
    removed_columns: int = 0
    changed_fields: int = 0
    change_rate: float = 0.0
    column_change_breakdown: Dict[str, int] = field(default_factory=dict)


def compute_stats(result: DiffResult, rows_a: int, rows_b: int) -> DiffStats:
    added = len(result.added_rows)
    removed = len(result.removed_rows)
    modified = len(result.modified_rows)
    added_cols = len(result.added_columns)
    removed_cols = len(result.removed_columns)

    changed_fields = 0
    column_breakdown: Dict[str, int] = {}
    for row_diff in result.modified_rows:
        for col, (old_val, new_val) in row_diff.get("changes", {}).items():
            changed_fields += 1
            column_breakdown[col] = column_breakdown.get(col, 0) + 1

    total = max(rows_a, rows_b, 1)
    change_rate = round((added + removed + modified) / total * 100, 2)

    return DiffStats(
        total_rows_a=rows_a,
        total_rows_b=rows_b,
        added_rows=added,
        removed_rows=removed,
        modified_rows=modified,
        added_columns=added_cols,
        removed_columns=removed_cols,
        changed_fields=changed_fields,
        change_rate=change_rate,
        column_change_breakdown=column_breakdown,
    )


def format_stats(stats: DiffStats) -> str:
    lines = [
        "=== Diff Statistics ===",
        f"Rows (A): {stats.total_rows_a}  Rows (B): {stats.total_rows_b}",
        f"Added rows: {stats.added_rows}",
        f"Removed rows: {stats.removed_rows}",
        f"Modified rows: {stats.modified_rows}",
        f"Added columns: {stats.added_columns}",
        f"Removed columns: {stats.removed_columns}",
        f"Changed fields: {stats.changed_fields}",
        f"Change rate: {stats.change_rate}%",
    ]
    if stats.column_change_breakdown:
        lines.append("Changes by column:")
        for col, count in sorted(stats.column_change_breakdown.items(), key=lambda x: -x[1]):
            lines.append(f"  {col}: {count}")
    return "\n".join(lines)
