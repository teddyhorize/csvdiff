"""Timeline: build a chronological sequence of diff events from multiple runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from csvdiff.differ import DiffResult


class TimelineError(Exception):
    """Raised when timeline operations fail."""


@dataclass
class TimelineEntry:
    timestamp: str
    label: str
    added: int
    removed: int
    modified: int
    added_columns: List[str] = field(default_factory=list)
    removed_columns: List[str] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return self.added + self.removed + self.modified

    @property
    def is_clean(self) -> bool:
        return self.total_changes == 0 and not self.added_columns and not self.removed_columns


@dataclass
class Timeline:
    entries: List[TimelineEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)


def _now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def add_entry(
    timeline: Timeline,
    result: DiffResult,
    label: str,
    timestamp: Optional[str] = None,
) -> TimelineEntry:
    """Append a new entry derived from *result* to *timeline*."""
    if not label:
        raise TimelineError("label must not be empty")
    entry = TimelineEntry(
        timestamp=timestamp or _now_iso(),
        label=label,
        added=len(result.added),
        removed=len(result.removed),
        modified=len(result.modified),
        added_columns=list(result.added_columns),
        removed_columns=list(result.removed_columns),
    )
    timeline.entries.append(entry)
    return entry


def format_timeline(timeline: Timeline, *, color: bool = False) -> str:
    """Render a human-readable timeline table."""
    if not timeline.entries:
        return "(no timeline entries)"

    lines = [f"{'Timestamp':<22} {'Label':<20} {'Added':>6} {'Removed':>8} {'Modified':>9}"]
    lines.append("-" * 70)
    for e in timeline.entries:
        lines.append(
            f"{e.timestamp:<22} {e.label:<20} {e.added:>6} {e.removed:>8} {e.modified:>9}"
        )
    return "\n".join(lines)
