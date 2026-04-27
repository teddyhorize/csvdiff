"""Baseline comparison: compare current diff against a saved baseline diff."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from csvdiff.differ import DiffResult


class BaselineError(Exception):
    pass


@dataclass
class BaselineComparison:
    new_regressions: list[str] = field(default_factory=list)
    resolved_issues: list[str] = field(default_factory=list)
    unchanged_issues: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.new_regressions) == 0


def _diff_to_dict(result: DiffResult) -> dict[str, Any]:
    return {
        "added": [dict(r) for r in result.added],
        "removed": [dict(r) for r in result.removed],
        "modified": [
            {"key": k, "old": dict(o), "new": dict(n)}
            for k, o, n in result.modified
        ],
    }


def save_baseline(result: DiffResult, path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(_diff_to_dict(result), fh, indent=2)


def load_baseline(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise BaselineError(f"Baseline file not found: {p}")
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def compare_to_baseline(result: DiffResult, path: str | Path) -> BaselineComparison:
    baseline = load_baseline(path)

    def _row_sig(row: dict) -> str:
        return json.dumps(row, sort_keys=True)

    baseline_added = {_row_sig(r) for r in baseline.get("added", [])}
    baseline_removed = {_row_sig(r) for r in baseline.get("removed", [])}
    baseline_modified = {
        json.dumps({"key": e["key"], "old": e["old"], "new": e["new"]}, sort_keys=True)
        for e in baseline.get("modified", [])
    }

    current_added = {_row_sig(dict(r)) for r in result.added}
    current_removed = {_row_sig(dict(r)) for r in result.removed}
    current_modified = {
        json.dumps({"key": k, "old": dict(o), "new": dict(n)}, sort_keys=True)
        for k, o, n in result.modified
    }

    all_baseline = baseline_added | baseline_removed | baseline_modified
    all_current = current_added | current_removed | current_modified

    return BaselineComparison(
        new_regressions=sorted(all_current - all_baseline),
        resolved_issues=sorted(all_baseline - all_current),
        unchanged_issues=sorted(all_baseline & all_current),
    )


def format_baseline_comparison(cmp: BaselineComparison) -> str:
    lines = []
    lines.append(f"New regressions : {len(cmp.new_regressions)}")
    lines.append(f"Resolved issues : {len(cmp.resolved_issues)}")
    lines.append(f"Unchanged issues: {len(cmp.unchanged_issues)}")
    if cmp.new_regressions:
        lines.append("\nNew regressions:")
        for r in cmp.new_regressions:
            lines.append(f"  {r}")
    return "\n".join(lines)
