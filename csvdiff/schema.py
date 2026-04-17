"""Schema comparison: detect column additions, removals, and reordering."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SchemaDiff:
    added_columns: List[str]
    removed_columns: List[str]
    reordered: bool
    left_columns: List[str]
    right_columns: List[str]

    @property
    def has_changes(self) -> bool:
        return bool(self.added_columns or self.removed_columns or self.reordered)


def compare_schemas(left_headers: List[str], right_headers: List[str]) -> SchemaDiff:
    """Compare two lists of column headers and return a SchemaDiff."""
    left_set = set(left_headers)
    right_set = set(right_headers)

    added = [c for c in right_headers if c not in left_set]
    removed = [c for c in left_headers if c not in right_set]

    common_left = [c for c in left_headers if c in right_set]
    common_right = [c for c in right_headers if c in left_set]
    reordered = common_left != common_right

    return SchemaDiff(
        added_columns=added,
        removed_columns=removed,
        reordered=reordered,
        left_columns=left_headers,
        right_columns=right_headers,
    )


def format_schema_diff(diff: SchemaDiff) -> str:
    """Return a human-readable string describing schema changes."""
    if not diff.has_changes:
        return "Schemas are identical."

    lines = []
    if diff.added_columns:
        lines.append(f"  Added columns:   {', '.join(diff.added_columns)}")
    if diff.removed_columns:
        lines.append(f"  Removed columns: {', '.join(diff.removed_columns)}")
    if diff.reordered:
        lines.append("  Column order changed.")
    return "Schema differences:\n" + "\n".join(lines)
