"""Similarity scoring between two CSV datasets."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
from csvdiff.differ import DiffResult


@dataclass
class SimilarityScore:
    total_rows: int
    matched_rows: int
    added: int
    removed: int
    modified: int
    score: float  # 0.0 to 1.0


def _total_rows(result: DiffResult) -> int:
    all_keys = (
        set(result.added)
        | set(result.removed)
        | set(result.modified)
        | set(result.unchanged)
    )
    return len(all_keys)


def compute_score(result: DiffResult) -> SimilarityScore:
    total = _total_rows(result)
    if total == 0:
        return SimilarityScore(
            total_rows=0,
            matched_rows=0,
            added=0,
            removed=0,
            modified=0,
            score=1.0,
        )
    unchanged = len(result.unchanged)
    added = len(result.added)
    removed = len(result.removed)
    modified = len(result.modified)
    score = round(unchanged / total, 4)
    return SimilarityScore(
        total_rows=total,
        matched_rows=unchanged,
        added=added,
        removed=removed,
        modified=modified,
        score=score,
    )


def format_score(s: SimilarityScore) -> str:
    pct = f"{s.score * 100:.1f}%"
    lines = [
        f"Similarity Score : {pct}",
        f"Total Rows       : {s.total_rows}",
        f"Matched (unchanged): {s.matched_rows}",
        f"Added            : {s.added}",
        f"Removed          : {s.removed}",
        f"Modified         : {s.modified}",
    ]
    return "\n".join(lines)
