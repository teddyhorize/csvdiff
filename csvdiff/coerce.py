"""Type coercion utilities for normalizing CSV column values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class CoerceError(Exception):
    """Raised when a coercion rule is invalid or fails unexpectedly."""


@dataclass
class CoerceOptions:
    """Options controlling which columns to coerce and to what type."""

    rules: Dict[str, str] = field(default_factory=dict)
    # Supported types: "int", "float", "bool", "str"
    on_error: str = "skip"  # "skip" | "raise" | "null"


_BOOL_TRUE = {"true", "1", "yes", "y", "on"}
_BOOL_FALSE = {"false", "0", "no", "n", "off"}


def _coerce_value(value: str, target_type: str) -> Any:
    """Attempt to coerce a single string value to the target type."""
    if target_type == "str":
        return value
    if target_type == "int":
        return int(value)
    if target_type == "float":
        return float(value)
    if target_type == "bool":
        lowered = value.strip().lower()
        if lowered in _BOOL_TRUE:
            return True
        if lowered in _BOOL_FALSE:
            return False
        raise ValueError(f"Cannot coerce {value!r} to bool")
    raise CoerceError(f"Unknown target type: {target_type!r}")


def coerce_row(
    row: Dict[str, str],
    options: CoerceOptions,
) -> Dict[str, Any]:
    """Return a new row with specified columns coerced to their target types."""
    result: Dict[str, Any] = dict(row)
    for column, target_type in options.rules.items():
        if column not in row:
            continue
        raw = row[column]
        try:
            result[column] = _coerce_value(raw, target_type)
        except (ValueError, TypeError) as exc:
            if options.on_error == "raise":
                raise CoerceError(
                    f"Failed to coerce column {column!r} value {raw!r} "
                    f"to {target_type!r}: {exc}"
                ) from exc
            elif options.on_error == "null":
                result[column] = None
            # else "skip": leave original string value
    return result


def coerce_rows(
    rows: List[Dict[str, str]],
    options: CoerceOptions,
) -> List[Dict[str, Any]]:
    """Apply coerce_row to every row in a list."""
    return [coerce_row(row, options) for row in rows]


def build_coerce_options(
    rules: Optional[Dict[str, str]] = None,
    on_error: str = "skip",
) -> CoerceOptions:
    """Convenience constructor for CoerceOptions."""
    if on_error not in ("skip", "raise", "null"):
        raise CoerceError(f"Invalid on_error value: {on_error!r}")
    return CoerceOptions(rules=rules or {}, on_error=on_error)
