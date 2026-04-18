"""Merge two CSV datasets, preferring values from the second on conflict."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class MergeError(Exception):
    pass


@dataclass
class MergeOptions:
    key_column: str
    prefer: str = "right"  # "left" or "right"
    fill_missing: bool = True


@dataclass
class MergeResult:
    rows: List[Dict[str, str]]
    conflicts_resolved: int = 0
    added_from_right: int = 0
    columns: List[str] = field(default_factory=list)


def _index(rows: List[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    if not rows:
        return {}
    return {r[key]: r for r in rows if key in r}


def merge_rows(
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    options: MergeOptions,
) -> MergeResult:
    key = options.key_column
    if left and key not in left[0]:
        raise MergeError(f"Key column '{key}' not found in left dataset")
    if right and key not in right[0]:
        raise MergeError(f"Key column '{key}' not found in right dataset")

    left_idx = _index(left, key)
    right_idx = _index(right, key)

    all_keys_left = [r[key] for r in left]
    seen = set()
    merged: List[Dict[str, str]] = []
    conflicts = 0
    added = 0

    left_cols = list(left[0].keys()) if left else []
    right_cols = list(right[0].keys()) if right else []
    all_cols = left_cols + [c for c in right_cols if c not in left_cols]

    for k in all_keys_left:
        seen.add(k)
        l_row = left_idx[k]
        if k in right_idx:
            r_row = right_idx[k]
            base = dict(l_row)
            for col, val in r_row.items():
                if col in base and base[col] != val:
                    conflicts += 1
                    if options.prefer == "right":
                        base[col] = val
                elif col not in base:
                    base[col] = val
            if options.fill_missing:
                for col in all_cols:
                    base.setdefault(col, "")
            merged.append(base)
        else:
            row = dict(l_row)
            if options.fill_missing:
                for col in all_cols:
                    row.setdefault(col, "")
            merged.append(row)

    for k, r_row in right_idx.items():
        if k not in seen:
            row = dict(r_row)
            if options.fill_missing:
                for col in all_cols:
                    row.setdefault(col, "")
            merged.append(row)
            added += 1

    return MergeResult(rows=merged, conflicts_resolved=conflicts, added_from_right=added, columns=all_cols)
