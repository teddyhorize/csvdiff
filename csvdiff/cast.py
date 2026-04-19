"""Type casting utilities for CSV cell values."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class CastError(Exception):
    pass


@dataclass
class CastOptions:
    int_columns: List[str] = field(default_factory=list)
    float_columns: List[str] = field(default_factory=list)
    bool_columns: List[str] = field(default_factory=list)
    strict: bool = False


_BOOL_TRUE = {"true", "1", "yes", "y"}
_BOOL_FALSE = {"false", "0", "no", "n"}


def _cast_value(value: str, typ: str, column: str, strict: bool) -> Any:
    try:
        if typ == "int":
            return int(value)
        if typ == "float":
            return float(value)
        if typ == "bool":
            lower = value.strip().lower()
            if lower in _BOOL_TRUE:
                return True
            if lower in _BOOL_FALSE:
                return False
            raise ValueError(f"Cannot parse bool: {value!r}")
    except (ValueError, TypeError) as exc:
        if strict:
            raise CastError(f"Column '{column}': {exc}") from exc
        return value
    return value


def cast_row(row: Dict[str, str], options: CastOptions) -> Dict[str, Any]:
    result = dict(row)
    for col in options.int_columns:
        if col in result:
            result[col] = _cast_value(result[col], "int", col, options.strict)
    for col in options.float_columns:
        if col in result:
            result[col] = _cast_value(result[col], "float", col, options.strict)
    for col in options.bool_columns:
        if col in result:
            result[col] = _cast_value(result[col], "bool", col, options.strict)
    return result


def cast_rows(
    rows: List[Dict[str, str]], options: Optional[CastOptions] = None
) -> List[Dict[str, Any]]:
    if options is None:
        return list(rows)
    return [cast_row(row, options) for row in rows]
