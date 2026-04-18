from dataclasses import dataclass, field
from typing import List, Optional


class SortError(Exception):
    pass


@dataclass
class SortOptions:
    columns: List[str] = field(default_factory=list)
    reverse: bool = False
    case_sensitive: bool = True


def _sort_key(row: dict, columns: List[str], case_sensitive: bool):
    parts = []
    for col in columns:
        val = row.get(col, "")
        if not case_sensitive:
            val = val.lower()
        parts.append(val)
    return parts


def sort_rows(
    rows: List[dict],
    options: Optional[SortOptions] = None,
) -> List[dict]:
    if options is None or not options.columns:
        return rows

    missing = [c for c in options.columns if rows and c not in rows[0]]
    if missing:
        raise SortError(f"Sort columns not found in data: {missing}")

    return sorted(
        rows,
        key=lambda r: _sort_key(r, options.columns, options.case_sensitive),
        reverse=options.reverse,
    )


def sort_pair(
    rows_a: List[dict],
    rows_b: List[dict],
    options: Optional[SortOptions] = None,
) -> tuple:
    return sort_rows(rows_a, options), sort_rows(rows_b, options)
