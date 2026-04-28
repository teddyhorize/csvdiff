"""Compute Shannon entropy for columns to detect randomness or uniformity."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class EntropyError(Exception):
    """Raised when entropy computation fails."""


@dataclass
class ColumnEntropy:
    column: str
    entropy: float
    unique_values: int
    total_values: int
    max_entropy: float

    @property
    def normalized(self) -> Optional[float]:
        """Entropy as a fraction of maximum possible entropy (0.0–1.0)."""
        if self.max_entropy == 0.0:
            return None
        return self.entropy / self.max_entropy


@dataclass
class EntropyResult:
    columns: List[ColumnEntropy] = field(default_factory=list)

    def get(self, column: str) -> Optional[ColumnEntropy]:
        for col in self.columns:
            if col.column == column:
                return col
        return None


def _shannon_entropy(values: List[str]) -> float:
    """Compute Shannon entropy in bits for a list of string values."""
    total = len(values)
    if total == 0:
        return 0.0
    counts = Counter(values)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def compute_entropy(
    rows: List[Dict[str, str]],
    columns: Optional[List[str]] = None,
) -> EntropyResult:
    """Compute Shannon entropy for each column in *rows*."""
    if not rows:
        return EntropyResult()

    all_columns = list(rows[0].keys())
    target_columns = columns if columns is not None else all_columns

    unknown = set(target_columns) - set(all_columns)
    if unknown:
        raise EntropyError(f"Unknown columns: {sorted(unknown)}")

    result = EntropyResult()
    for col in target_columns:
        values = [row.get(col, "") for row in rows]
        entropy = _shannon_entropy(values)
        unique = len(set(values))
        total = len(values)
        max_entropy = math.log2(unique) if unique > 1 else 0.0
        result.columns.append(
            ColumnEntropy(
                column=col,
                entropy=round(entropy, 6),
                unique_values=unique,
                total_values=total,
                max_entropy=round(max_entropy, 6),
            )
        )
    return result


def format_entropy(result: EntropyResult) -> str:
    """Return a human-readable table of entropy results."""
    if not result.columns:
        return "No entropy data."
    lines = [f"{'Column':<24} {'Entropy':>10} {'Normalized':>12} {'Unique':>8}"]
    lines.append("-" * 58)
    for col in result.columns:
        norm = f"{col.normalized:.4f}" if col.normalized is not None else "  N/A"
        lines.append(
            f"{col.column:<24} {col.entropy:>10.4f} {norm:>12} {col.unique_values:>8}"
        )
    return "\n".join(lines)
