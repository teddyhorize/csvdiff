"""Split a CSV diff result into multiple output files by change type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import csv
import io

from csvdiff.differ import DiffResult


class SplitError(Exception):
    """Raised when a split operation fails."""


@dataclass
class SplitOptions:
    output_dir: str = "."
    prefix: str = "diff"
    include_unchanged: bool = False


@dataclass
class SplitResult:
    added_path: Optional[str] = None
    removed_path: Optional[str] = None
    modified_path: Optional[str] = None
    unchanged_path: Optional[str] = None
    files_written: List[str] = field(default_factory=list)


def _rows_to_csv(rows: List[dict], fieldnames: List[str]) -> str:
    """Serialize a list of row dicts to a CSV string."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def _write_file(path: str, content: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write(content)


def split_diff(
    result: DiffResult,
    headers: List[str],
    options: Optional[SplitOptions] = None,
) -> SplitResult:
    """Write each change category to its own CSV file."""
    if options is None:
        options = SplitOptions()

    out = SplitResult()
    base = f"{options.output_dir}/{options.prefix}"

    categories = [
        ("added", result.added_rows),
        ("removed", result.removed_rows),
        ("modified", [r["new"] for r in result.modified_rows]),
    ]

    for label, rows in categories:
        if not rows:
            continue
        path = f"{base}_{label}.csv"
        _write_file(path, _rows_to_csv(rows, headers))
        out.files_written.append(path)
        setattr(out, f"{label}_path", path)

    if options.include_unchanged and result.unchanged_rows:
        path = f"{base}_unchanged.csv"
        _write_file(path, _rows_to_csv(result.unchanged_rows, headers))
        out.unchanged_path = path
        out.files_written.append(path)

    return out


def format_split_result(result: SplitResult) -> str:
    """Return a human-readable summary of written files."""
    if not result.files_written:
        return "No files written (no differences found)."
    lines = ["Split output:"]
    for path in result.files_written:
        lines.append(f"  {path}")
    return "\n".join(lines)
