"""Core diffing logic for comparing two parsed CSV files."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiffResult:
    added_rows: list[dict[str, Any]] = field(default_factory=list)
    removed_rows: list[dict[str, Any]] = field(default_factory=list)
    modified_rows: list[dict[str, tuple[Any, Any]]] = field(default_factory=list)
    added_columns: list[str] = field(default_factory=list)
    removed_columns: list[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.added_rows
            or self.removed_rows
            or self.modified_rows
            or self.added_columns
            or self.removed_columns
        )

    def summary(self) -> str:
        """Return a human-readable summary of the diff."""
        parts = []
        if self.added_rows:
            parts.append(f"{len(self.added_rows)} row(s) added")
        if self.removed_rows:
            parts.append(f"{len(self.removed_rows)} row(s) removed")
        if self.modified_rows:
            parts.append(f"{len(self.modified_rows)} row(s) modified")
        if self.added_columns:
            parts.append(f"{len(self.added_columns)} column(s) added")
        if self.removed_columns:
            parts.append(f"{len(self.removed_columns)} column(s) removed")
        return ", ".join(parts) if parts else "No differences"


def diff_csv(
    left: list[dict[str, str]],
    right: list[dict[str, str]],
    key: str | None = None,
) -> DiffResult:
    """Compare two lists of CSV rows and return a DiffResult.

    Args:
        left: Rows from the original CSV file.
        right: Rows from the new CSV file.
        key: Column name to use as a unique row identifier. If None, row
             index is used for alignment.
    """
    result = DiffResult()

    left_cols = set(left[0].keys()) if left else set()
    right_cols = set(right[0].keys()) if right else set()
    result.added_columns = sorted(right_cols - left_cols)
    result.removed_columns = sorted(left_cols - right_cols)

    if key:
        if left and key not in left[0]:
            raise KeyError(f"Key column '{key}' not found in left CSV")
        if right and key not in right[0]:
            raise KeyError(f"Key column '{key}' not found in right CSV")

        left_map = {row[key]: row for row in left}
        right_map = {row[key]: row for row in right}

        for k, row in right_map.items():
            if k not in left_map:
                result.added_rows.append(row)

        for k, row in left_map.items():
            if k not in right_map:
                result.removed_rows.append(row)
            else:
                changes = {
                    col: (row[col], right_map[k][col])
                    for col in (left_cols & right_cols)
                    if row[col] != right_map[k][col]
                }
                if changes:
                    result.modified_rows.append(changes)
    else:
        common_len = min(len(left), len(right))
        shared_cols = left_cols & right_cols

        for i in range(common_len):
            changes = {
                col: (left[i][col], right[i][col])
                for col in shared_cols
                if left[i][col] != right[i][col]
            }
            if changes:
                result.modified_rows.append(changes)

        result.added_rows = right[common_len:]
        result.removed_rows = left[common_len:]

    return result
