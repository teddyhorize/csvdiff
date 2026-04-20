"""Redact sensitive columns from CSV rows before diffing or display."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


class RedactError(Exception):
    """Raised when redaction configuration is invalid."""


@dataclass
class RedactOptions:
    columns: List[str] = field(default_factory=list)
    placeholder: str = "***"


def _validate(options: RedactOptions) -> None:
    if not options.placeholder:
        raise RedactError("Redaction placeholder must not be empty.")


def redact_row(
    row: Dict[str, Any],
    options: RedactOptions,
) -> Dict[str, Any]:
    """Return a copy of *row* with sensitive columns replaced by the placeholder."""
    _validate(options)
    if not options.columns:
        return dict(row)
    return {
        key: (options.placeholder if key in options.columns else value)
        for key, value in row.items()
    }


def redact_rows(
    rows: List[Dict[str, Any]],
    options: RedactOptions,
) -> List[Dict[str, Any]]:
    """Apply redaction to every row in *rows*."""
    return [redact_row(row, options) for row in rows]


def redact_pair(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    options: RedactOptions,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Redact both sides of a CSV pair in one call."""
    return redact_rows(left, options), redact_rows(right, options)
