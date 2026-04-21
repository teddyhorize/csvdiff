"""Track column/row lineage across transformations for audit trails."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict


class LineageError(Exception):
    """Raised when lineage tracking fails."""


@dataclass
class LineageEvent:
    step: str
    description: str
    affected_columns: List[str] = field(default_factory=list)
    affected_rows: int = 0


@dataclass
class Lineage:
    source_file: str
    events: List[LineageEvent] = field(default_factory=list)

    def add(self, step: str, description: str,
            affected_columns: Optional[List[str]] = None,
            affected_rows: int = 0) -> None:
        self.events.append(LineageEvent(
            step=step,
            description=description,
            affected_columns=affected_columns or [],
            affected_rows=affected_rows,
        ))


def build_lineage(source_file: str) -> Lineage:
    """Create a new Lineage tracker for a source file."""
    if not source_file:
        raise LineageError("source_file must not be empty")
    return Lineage(source_file=source_file)


def record_rename(lineage: Lineage, mapping: Dict[str, str]) -> None:
    """Record a rename transformation event."""
    cols = [f"{old}->{new}" for old, new in mapping.items()]
    lineage.add("rename", f"Renamed {len(cols)} column(s)", affected_columns=cols)


def record_filter(lineage: Lineage, removed_rows: int, reason: str = "") -> None:
    """Record a row filter event."""
    desc = f"Filtered {removed_rows} row(s)"
    if reason:
        desc += f": {reason}"
    lineage.add("filter", desc, affected_rows=removed_rows)


def format_lineage(lineage: Lineage) -> str:
    """Render lineage as a human-readable string."""
    lines = [f"Lineage for: {lineage.source_file}"]
    if not lineage.events:
        lines.append("  (no transformations recorded)")
        return "\n".join(lines)
    for i, ev in enumerate(lineage.events, 1):
        lines.append(f"  {i}. [{ev.step}] {ev.description}")
        if ev.affected_columns:
            lines.append(f"     columns: {', '.join(ev.affected_columns)}")
        if ev.affected_rows:
            lines.append(f"     rows affected: {ev.affected_rows}")
    return "\n".join(lines)
