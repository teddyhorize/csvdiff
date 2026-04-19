"""Column profiling: compute per-column statistics for CSV data."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ColumnProfile:
    name: str
    count: int = 0
    empty_count: int = 0
    unique_values: int = 0
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    sample_values: List[str] = field(default_factory=list)

    @property
    def fill_rate(self) -> float:
        if self.count == 0:
            return 0.0
        return round((self.count - self.empty_count) / self.count, 4)


@dataclass
class ProfileResult:
    columns: Dict[str, ColumnProfile] = field(default_factory=dict)


MAX_SAMPLES = 5


def profile_rows(rows: List[Dict[str, str]]) -> ProfileResult:
    """Compute a ColumnProfile for each column found in rows."""
    if not rows:
        return ProfileResult()

    headers = list(rows[0].keys())
    profiles: Dict[str, ColumnProfile] = {h: ColumnProfile(name=h) for h in headers}
    seen: Dict[str, set] = {h: set() for h in headers}

    for row in rows:
        for col in headers:
            val = row.get(col, "")
            p = profiles[col]
            p.count += 1
            if val == "" or val is None:
                p.empty_count += 1
            else:
                length = len(val)
                p.min_length = length if p.min_length is None else min(p.min_length, length)
                p.max_length = length if p.max_length is None else max(p.max_length, length)
                seen[col].add(val)
                if len(p.sample_values) < MAX_SAMPLES and val not in p.sample_values:
                    p.sample_values.append(val)

    for col, vals in seen.items():
        profiles[col].unique_values = len(vals)

    return ProfileResult(columns=profiles)


def format_profile(result: ProfileResult) -> str:
    """Render a ProfileResult as a human-readable string."""
    if not result.columns:
        return "No columns to profile."
    lines = []
    for name, p in result.columns.items():
        lines.append(f"Column: {name}")
        lines.append(f"  Rows      : {p.count}")
        lines.append(f"  Empty     : {p.empty_count}")
        lines.append(f"  Fill rate : {p.fill_rate:.1%}")
        lines.append(f"  Unique    : {p.unique_values}")
        lines.append(f"  Length    : {p.min_length}–{p.max_length}")
        lines.append(f"  Samples   : {', '.join(p.sample_values)}")
    return "\n".join(lines)
