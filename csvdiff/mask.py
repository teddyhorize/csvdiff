"""Mask module: partially obscure cell values for privacy or display purposes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class MaskError(Exception):
    """Raised when masking configuration is invalid."""


@dataclass
class MaskOptions:
    columns: List[str] = field(default_factory=list)
    placeholder: str = "***"
    keep_start: int = 0
    keep_end: int = 0


def _validate(opts: MaskOptions) -> None:
    if opts.keep_start < 0 or opts.keep_end < 0:
        raise MaskError("keep_start and keep_end must be non-negative")
    if not opts.placeholder:
        raise MaskError("placeholder must not be empty")


def mask_value(value: str, opts: MaskOptions) -> str:
    """Partially mask a single string value."""
    _validate(opts)
    n = len(value)
    start = min(opts.keep_start, n)
    end = min(opts.keep_end, n - start)
    if end == 0:
        return value[:start] + opts.placeholder if start < n else value
    return value[:start] + opts.placeholder + value[n - end :]


def mask_row(
    row: Dict[str, str], opts: MaskOptions
) -> Dict[str, str]:
    """Return a copy of *row* with specified columns masked."""
    _validate(opts)
    result = dict(row)
    for col in opts.columns:
        if col in result:
            result[col] = mask_value(result[col], opts)
    return result


def mask_rows(
    rows: List[Dict[str, str]], opts: Optional[MaskOptions] = None
) -> List[Dict[str, str]]:
    """Apply masking to every row in *rows*."""
    if opts is None or not opts.columns:
        return rows
    return [mask_row(r, opts) for r in rows]
