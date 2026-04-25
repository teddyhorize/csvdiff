"""Fingerprinting module: generate stable hashes for CSV row sets."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import List, Dict, Optional

from csvdiff.differ import DiffResult


class FingerprintError(Exception):
    """Raised when fingerprinting fails."""


@dataclass
class Fingerprint:
    left_hash: str
    right_hash: str
    diff_hash: str
    row_count_left: int
    row_count_right: int

    @property
    def is_identical(self) -> bool:
        return self.left_hash == self.right_hash


def _hash_rows(rows: List[Dict[str, str]]) -> str:
    """Return a stable SHA-256 hex digest for a list of row dicts."""
    serialized = json.dumps(rows, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _hash_diff(result: DiffResult) -> str:
    """Hash the structural diff (added/removed/modified keys)."""
    payload = {
        "added": sorted(result.added_rows, key=lambda r: json.dumps(r, sort_keys=True)),
        "removed": sorted(result.removed_rows, key=lambda r: json.dumps(r, sort_keys=True)),
        "modified": [
            {"key": k, "old": o, "new": n}
            for k, o, n in sorted(result.modified_rows, key=lambda t: str(t[0]))
        ],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()


def compute_fingerprint(
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    result: DiffResult,
) -> Fingerprint:
    """Compute a Fingerprint from two row sets and their diff."""
    if left is None or right is None:
        raise FingerprintError("Row lists must not be None.")
    return Fingerprint(
        left_hash=_hash_rows(left),
        right_hash=_hash_rows(right),
        diff_hash=_hash_diff(result),
        row_count_left=len(left),
        row_count_right=len(right),
    )


def format_fingerprint(fp: Fingerprint, *, color: bool = False) -> str:
    """Return a human-readable summary of a Fingerprint."""
    status = "identical" if fp.is_identical else "changed"
    lines = [
        f"Status     : {status}",
        f"Left hash  : {fp.left_hash[:16]}...",
        f"Right hash : {fp.right_hash[:16]}...",
        f"Diff hash  : {fp.diff_hash[:16]}...",
        f"Rows left  : {fp.row_count_left}",
        f"Rows right : {fp.row_count_right}",
    ]
    return "\n".join(lines)
