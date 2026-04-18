"""Normalization options and transforms for CSV values before diffing."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict


class NormalizeError(Exception):
    pass


@dataclass
class NormalizeOptions:
    strip_whitespace: bool = True
    lowercase: bool = False
    columns: List[str] = field(default_factory=list)  # empty = all columns


def _normalize_value(value: str, opts: NormalizeOptions) -> str:
    if opts.strip_whitespace:
        value = value.strip()
    if opts.lowercase:
        value = value.lower()
    return value


def normalize_row(row: Dict[str, str], opts: NormalizeOptions) -> Dict[str, str]:
    """Return a new row dict with normalized values."""
    target = set(opts.columns) if opts.columns else None
    if target is not None:
        unknown = target - row.keys()
        if unknown:
            raise NormalizeError(
                f"normalize_columns references unknown column(s): {', '.join(sorted(unknown))}"
            )
    return {
        k: (_normalize_value(v, opts) if (target is None or k in target) else v)
        for k, v in row.items()
    }


def normalize_rows(
    rows: List[Dict[str, str]], opts: NormalizeOptions
) -> List[Dict[str, str]]:
    return [normalize_row(r, opts) for r in rows]


def normalize_options_from_args(args) -> NormalizeOptions:
    """Build NormalizeOptions from parsed CLI args namespace."""
    return NormalizeOptions(
        strip_whitespace=not getattr(args, "no_strip", False),
        lowercase=getattr(args, "normalize_lowercase", False),
        columns=getattr(args, "normalize_columns", []) or [],
    )
