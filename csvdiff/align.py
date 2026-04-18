"""Column alignment utilities for side-by-side CSV comparison."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


class AlignError(Exception):
    pass


@dataclass
class AlignOptions:
    pad_char: str = " "
    min_width: int = 4
    max_width: int = 40
    truncate_long: bool = True


@dataclass
class AlignedTable:
    headers: List[str]
    rows: List[List[str]]
    widths: List[int] = field(default_factory=list)


def _col_width(header: str, rows: List[List[str]], col_idx: int, opts: AlignOptions) -> int:
    values = [header] + [r[col_idx] if col_idx < len(r) else "" for r in rows]
    raw = max(len(v) for v in values)
    return max(opts.min_width, min(raw, opts.max_width))


def compute_widths(headers: List[str], rows: List[List[str]], opts: Optional[AlignOptions] = None) -> List[int]:
    opts = opts or AlignOptions()
    if not headers:
        return []
    return [_col_width(headers[i], rows, i, opts) for i in range(len(headers))]


def pad_cell(value: str, width: int, opts: Optional[AlignOptions] = None) -> str:
    opts = opts or AlignOptions()
    if opts.truncate_long and len(value) > width:
        return value[: width - 1] + "…"
    return value.ljust(width, opts.pad_char)


def align_table(
    headers: List[str],
    rows: List[Dict[str, str]],
    opts: Optional[AlignOptions] = None,
) -> AlignedTable:
    opts = opts or AlignOptions()
    if not headers:
        raise AlignError("headers must not be empty")

    raw_rows = [[row.get(h, "") for h in headers] for row in rows]
    widths = compute_widths(headers, raw_rows, opts)

    padded_rows = [
        [pad_cell(cell, widths[i], opts) for i, cell in enumerate(r)]
        for r in raw_rows
    ]
    padded_headers = [pad_cell(h, widths[i], opts) for i, h in enumerate(headers)]

    return AlignedTable(headers=padded_headers, rows=padded_rows, widths=widths)


def render_table(table: AlignedTable, separator: str = "  ") -> str:
    lines = []
    header_line = separator.join(table.headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    for row in table.rows:
        lines.append(separator.join(row))
    return "\n".join(lines)
