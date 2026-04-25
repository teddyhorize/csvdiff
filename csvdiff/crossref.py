"""Cross-reference two CSV files by a shared key column."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class CrossRefError(Exception):
    """Raised when cross-reference cannot be performed."""


@dataclass
class CrossRefResult:
    key_column: str
    only_in_left: List[str] = field(default_factory=list)
    only_in_right: List[str] = field(default_factory=list)
    in_both: List[str] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.only_in_left) + len(self.only_in_right) + len(self.in_both)


def _extract_keys(
    rows: List[Dict[str, str]], key_column: str
) -> List[str]:
    if not rows:
        return []
    if key_column not in rows[0]:
        raise CrossRefError(
            f"Key column '{key_column}' not found in headers: "
            f"{list(rows[0].keys())}"
        )
    return [row[key_column] for row in rows]


def cross_reference(
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    key_column: str,
) -> CrossRefResult:
    """Compare two sets of rows by a shared key column."""
    if not key_column:
        raise CrossRefError("key_column must not be empty.")

    left_keys = set(_extract_keys(left, key_column))
    right_keys = set(_extract_keys(right, key_column))

    return CrossRefResult(
        key_column=key_column,
        only_in_left=sorted(left_keys - right_keys),
        only_in_right=sorted(right_keys - left_keys),
        in_both=sorted(left_keys & right_keys),
    )


def format_crossref(
    result: CrossRefResult, *, use_color: bool = False
) -> str:
    """Return a human-readable summary of the cross-reference result."""
    lines = [f"Cross-reference on '{result.key_column}'"]
    lines.append(f"  Keys in both   : {len(result.in_both)}")
    lines.append(f"  Only in left   : {len(result.only_in_left)}")
    lines.append(f"  Only in right  : {len(result.only_in_right)}")
    if result.only_in_left:
        lines.append("  Left-only keys : " + ", ".join(result.only_in_left))
    if result.only_in_right:
        lines.append("  Right-only keys: " + ", ".join(result.only_in_right))
    return "\n".join(lines)
