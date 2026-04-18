"""CLI helpers for printing diff statistics."""
from typing import List, Dict, Any
from csvdiff.differ import DiffResult
from csvdiff.stats import compute_stats, format_stats


def print_stats(result: DiffResult, rows_a: int, rows_b: int, use_color: bool = False) -> None:
    """Compute and print diff statistics to stdout."""
    stats = compute_stats(result, rows_a, rows_b)
    output = format_stats(stats)
    if use_color:
        output = _apply_color(output)
    print(output)


def _apply_color(text: str) -> str:
    """Apply simple ANSI colors to stats output."""
    colored_lines = []
    for line in text.split("\n"):
        if line.startswith("==="):
            line = f"\033[1;36m{line}\033[0m"
        elif line.startswith("Added rows") or line.startswith("Added columns"):
            line = f"\033[32m{line}\033[0m"
        elif line.startswith("Removed rows") or line.startswith("Removed columns"):
            line = f"\033[31m{line}\033[0m"
        elif line.startswith("Modified rows") or line.startswith("Changed fields"):
            line = f"\033[33m{line}\033[0m"
        colored_lines.append(line)
    return "\n".join(colored_lines)


def stats_as_dict(result: DiffResult, rows_a: int, rows_b: int) -> Dict[str, Any]:
    """Return stats as a plain dictionary for export or further processing."""
    stats = compute_stats(result, rows_a, rows_b)
    return {
        "total_rows_a": stats.total_rows_a,
        "total_rows_b": stats.total_rows_b,
        "added_rows": stats.added_rows,
        "removed_rows": stats.removed_rows,
        "modified_rows": stats.modified_rows,
        "added_columns": stats.added_columns,
        "removed_columns": stats.removed_columns,
        "changed_fields": stats.changed_fields,
        "change_rate": stats.change_rate,
        "column_change_breakdown": stats.column_change_breakdown,
    }
