"""Group rows by a column value and compute per-group diff counts."""
from dataclasses import dataclass, field
from typing import Dict, List
from csvdiff.differ import DiffResult


class GroupError(Exception):
    pass


@dataclass
class GroupStats:
    group_by: str
    added: Dict[str, int] = field(default_factory=dict)
    removed: Dict[str, int] = field(default_factory=dict)
    modified: Dict[str, int] = field(default_factory=dict)


def _get_key(row: dict, column: str) -> str:
    return str(row.get(column, "__missing__"))


def group_diff(result: DiffResult, column: str) -> GroupStats:
    if not column:
        raise GroupError("column must not be empty")
    stats = GroupStats(group_by=column)
    for row in result.added_rows:
        k = _get_key(row, column)
        stats.added[k] = stats.added.get(k, 0) + 1
    for row in result.removed_rows:
        k = _get_key(row, column)
        stats.removed[k] = stats.removed.get(k, 0) + 1
    for old, _new in result.modified_rows:
        k = _get_key(old, column)
        stats.modified[k] = stats.modified.get(k, 0) + 1
    return stats


def all_groups(stats: GroupStats) -> List[str]:
    keys = set(stats.added) | set(stats.removed) | set(stats.modified)
    return sorted(keys)


def format_group_stats(stats: GroupStats) -> str:
    lines = [f"Grouped by '{stats.group_by}':", ""]
    groups = all_groups(stats)
    if not groups:
        lines.append("  (no differences)")
        return "\n".join(lines)
    for g in groups:
        a = stats.added.get(g, 0)
        r = stats.removed.get(g, 0)
        m = stats.modified.get(g, 0)
        lines.append(f"  {g}: +{a} -{r} ~{m}")
    return "\n".join(lines)
