"""Context lines around diffs — show N rows before/after each changed row."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Set

from csvdiff.differ import DiffResult


class ContextError(Exception):
    """Raised when context options are invalid."""


@dataclass
class ContextOptions:
    lines: int = 2  # number of context rows before/after each change


@dataclass
class ContextWindow:
    changed_key: str
    before: List[Dict[str, Any]] = field(default_factory=list)
    changed: Dict[str, Any] = field(default_factory=dict)
    after: List[Dict[str, Any]] = field(default_factory=list)
    change_type: str = "modified"  # added | removed | modified


def _validate(opts: ContextOptions) -> None:
    if opts.lines < 0:
        raise ContextError(f"lines must be >= 0, got {opts.lines}")


def _changed_keys(result: DiffResult) -> Set[str]:
    keys: Set[str] = set()
    for row in result.added:
        keys.add(str(row))
    for row in result.removed:
        keys.add(str(row))
    for key in result.modified:
        keys.add(key)
    return keys


def build_context_windows(
    rows: List[Dict[str, Any]],
    result: DiffResult,
    key_column: str,
    opts: ContextOptions,
) -> List[ContextWindow]:
    """Return context windows for each changed row in *rows*."""
    _validate(opts)

    # Index rows by key for quick lookup
    indexed: Dict[str, int] = {r.get(key_column, ""): i for i, r in enumerate(rows)}

    windows: List[ContextWindow] = []

    def _window(row: Dict[str, Any], change_type: str) -> ContextWindow:
        key = row.get(key_column, "")
        idx = indexed.get(str(key), -1)
        before: List[Dict[str, Any]] = []
        after: List[Dict[str, Any]] = []
        if idx >= 0:
            start = max(0, idx - opts.lines)
            end = min(len(rows), idx + opts.lines + 1)
            before = rows[start:idx]
            after = rows[idx + 1 : end]
        return ContextWindow(
            changed_key=str(key),
            before=before,
            changed=row,
            after=after,
            change_type=change_type,
        )

    for row in result.added:
        windows.append(_window(row, "added"))
    for row in result.removed:
        windows.append(_window(row, "removed"))
    for key, change in result.modified.items():
        old = change.get("old", {})
        windows.append(_window(old, "modified"))

    return windows


def format_context(windows: List[ContextWindow], key_column: str) -> str:
    """Render context windows as a human-readable string."""
    if not windows:
        return "No changed rows with context."
    parts: List[str] = []
    for w in windows:
        tag = f"[{w.change_type.upper()}] key={w.changed_key}"
        block = [tag]
        for r in w.before:
            block.append(f"  context | {r}")
        block.append(f"  >>> {w.change_type} | {w.changed}")
        for r in w.after:
            block.append(f"  context | {r}")
        parts.append("\n".join(block))
    return "\n\n".join(parts)
