"""Summary statistics for CSV diff results."""
from dataclasses import dataclass
from csvdiff.differ import DiffResult


@dataclass
class DiffSummary:
    added_rows: int
    removed_rows: int
    modified_rows: int
    added_columns: list
    removed_columns: list
    total_changes: int

    def is_clean(self) -> bool:
        return self.total_changes == 0

    def as_dict(self) -> dict:
        return {
            "added_rows": self.added_rows,
            "removed_rows": self.removed_rows,
            "modified_rows": self.modified_rows,
            "added_columns": self.added_columns,
            "removed_columns": self.removed_columns,
            "total_changes": self.total_changes,
        }


def summarize(result: DiffResult) -> DiffSummary:
    """Compute a summary of a DiffResult."""
    added = len(result.added_rows)
    removed = len(result.removed_rows)
    modified = len(result.modified_rows)
    added_cols = list(result.added_columns)
    removed_cols = list(result.removed_columns)
    total = added + removed + modified + len(added_cols) + len(removed_cols)
    return DiffSummary(
        added_rows=added,
        removed_rows=removed,
        modified_rows=modified,
        added_columns=added_cols,
        removed_columns=removed_cols,
        total_changes=total,
    )


def format_summary(summary: DiffSummary) -> str:
    """Return a human-readable summary string."""
    if summary.is_clean():
        return "No differences found."
    lines = ["Summary:"]
    if summary.added_rows:
        lines.append(f"  Rows added:    {summary.added_rows}")
    if summary.removed_rows:
        lines.append(f"  Rows removed:  {summary.removed_rows}")
    if summary.modified_rows:
        lines.append(f"  Rows modified: {summary.modified_rows}")
    if summary.added_columns:
        lines.append(f"  Columns added:   {', '.join(summary.added_columns)}")
    if summary.removed_columns:
        lines.append(f"  Columns removed: {', '.join(summary.removed_columns)}")
    lines.append(f"  Total changes: {summary.total_changes}")
    return "\n".join(lines)
