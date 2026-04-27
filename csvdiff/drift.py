"""Detect schema and value drift between a baseline snapshot and current data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult
from csvdiff.schema import SchemaDiff, compare_schemas


class DriftError(Exception):
    """Raised when drift detection fails."""


@dataclass
class DriftReport:
    schema_drift: SchemaDiff
    added_rows: int
    removed_rows: int
    modified_rows: int
    changed_columns: Dict[str, int] = field(default_factory=dict)
    label: str = ""

    @property
    def has_drift(self) -> bool:
        return (
            self.schema_drift.has_changes()
            or self.added_rows > 0
            or self.removed_rows > 0
            or self.modified_rows > 0
        )


def detect_drift(
    old_headers: List[str],
    new_headers: List[str],
    result: DiffResult,
    label: str = "",
) -> DriftReport:
    """Produce a DriftReport from a DiffResult and header lists."""
    schema = compare_schemas(old_headers, new_headers)

    changed_columns: Dict[str, int] = {}
    for row in result.modified:
        old = row.get("old", {})
        new = row.get("new", {})
        all_keys = set(old) | set(new)
        for col in all_keys:
            if old.get(col) != new.get(col):
                changed_columns[col] = changed_columns.get(col, 0) + 1

    return DriftReport(
        schema_drift=schema,
        added_rows=len(result.added),
        removed_rows=len(result.removed),
        modified_rows=len(result.modified),
        changed_columns=changed_columns,
        label=label,
    )


def format_drift(report: DriftReport, color: bool = False) -> str:
    """Return a human-readable summary of the drift report."""
    lines: List[str] = []
    prefix = f"[{report.label}] " if report.label else ""

    if not report.has_drift:
        return f"{prefix}No drift detected."

    lines.append(f"{prefix}Drift detected:")
    if report.added_rows:
        lines.append(f"  Added rows    : {report.added_rows}")
    if report.removed_rows:
        lines.append(f"  Removed rows  : {report.removed_rows}")
    if report.modified_rows:
        lines.append(f"  Modified rows : {report.modified_rows}")
    if report.schema_drift.has_changes():
        if report.schema_drift.added_columns:
            lines.append(f"  New columns   : {', '.join(report.schema_drift.added_columns)}")
        if report.schema_drift.removed_columns:
            lines.append(f"  Dropped cols  : {', '.join(report.schema_drift.removed_columns)}")
    if report.changed_columns:
        top = sorted(report.changed_columns.items(), key=lambda x: -x[1])[:5]
        cols = ", ".join(f"{c}({n})" for c, n in top)
        lines.append(f"  Hot columns   : {cols}")
    return "\n".join(lines)
