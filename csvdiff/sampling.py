"""Random and systematic sampling of CSV rows."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Dict, Optional


class SamplingError(Exception):
    pass


@dataclass
class SamplingOptions:
    n: Optional[int] = None          # take exactly n rows
    fraction: Optional[float] = None  # take a fraction 0.0–1.0
    seed: Optional[int] = None
    systematic: bool = False          # evenly spaced instead of random


def _validate(opts: SamplingOptions) -> None:
    if opts.n is not None and opts.fraction is not None:
        raise SamplingError("Specify either 'n' or 'fraction', not both.")
    if opts.fraction is not None and not (0.0 < opts.fraction <= 1.0):
        raise SamplingError("fraction must be between 0 (exclusive) and 1 (inclusive).")
    if opts.n is not None and opts.n < 1:
        raise SamplingError("n must be >= 1.")


def sample_rows(
    rows: List[Dict[str, str]],
    opts: SamplingOptions,
) -> List[Dict[str, str]]:
    """Return a sampled subset of rows according to opts."""
    _validate(opts)
    if not rows:
        return []

    total = len(rows)
    n = opts.n if opts.n is not None else max(1, round((opts.fraction or 1.0) * total))
    n = min(n, total)

    if opts.systematic:
        step = total / n
        indices = [int(i * step) for i in range(n)]
        return [rows[i] for i in indices]

    rng = random.Random(opts.seed)
    return rng.sample(rows, n)


def sample_pair(
    rows_a: List[Dict[str, str]],
    rows_b: List[Dict[str, str]],
    opts: SamplingOptions,
) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Apply the same logical sampling to two row sets."""
    return sample_rows(rows_a, opts), sample_rows(rows_b, opts)
