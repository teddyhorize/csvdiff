"""Export diff results to various output formats."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from typing import Literal

from csvdiff.differ import DiffResult

OutputFormat = Literal["json", "csv", "markdown"]


@dataclass
class ExportOptions:
    format: OutputFormat = "json"
    indent: int = 2


def export_json(result: DiffResult, indent: int = 2) -> str:
    data = {
        "added_rows": result.added_rows,
        "removed_rows": result.removed_rows,
        "modified_rows": [
            {"key": k, "before": b, "after": a}
            for k, b, a in result.modified_rows
        ],
        "added_columns": result.added_columns,
        "removed_columns": result.removed_columns,
    }
    return json.dumps(data, indent=indent)


def export_csv(result: DiffResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["change_type", "key", "field", "old_value", "new_value"])

    for row in result.added_rows:
        writer.writerow(["added", "", "", "", json.dumps(row)])

    for row in result.removed_rows:
        writer.writerow(["removed", "", "", json.dumps(row), ""])

    for key, before, after in result.modified_rows:
        for field in set(before) | set(after):
            old_val = before.get(field, "")
            new_val = after.get(field, "")
            if old_val != new_val:
                writer.writerow(["modified", key, field, old_val, new_val])

    for col in result.added_columns:
        writer.writerow(["added_column", "", col, "", ""])

    for col in result.removed_columns:
        writer.writerow(["removed_column", "", col, "", ""])

    return buf.getvalue()


def export_markdown(result: DiffResult) -> str:
    lines = ["# CSV Diff Report", ""]

    if result.added_columns:
        lines += ["## Added Columns", ""] + [f"- `{c}`" for c in result.added_columns] + [""]
    if result.removed_columns:
        lines += ["## Removed Columns", ""] + [f"- `{c}`" for c in result.removed_columns] + [""]
    if result.added_rows:
        lines += ["## Added Rows", ""] + [f"- {r}" for r in result.added_rows] + [""]
    if result.removed_rows:
        lines += ["## Removed Rows", ""] + [f"- {r}" for r in result.removed_rows] + [""]
    if result.modified_rows:
        lines += ["## Modified Rows", ""]
        for key, before, after in result.modified_rows:
            lines.append(f"### Key: `{key}`")
            lines.append("| Field | Before | After |")
            lines.append("|-------|--------|-------|")
            for field in set(before) | set(after):
                if before.get(field) != after.get(field):
                    lines.append(f"| {field} | {before.get(field, '')} | {after.get(field, '')} |")
            lines.append("")
    return "\n".join(lines)


def export_diff(result: DiffResult, options: ExportOptions | None = None) -> str:
    options = options or ExportOptions()
    if options.format == "json":
        return export_json(result, indent=options.indent)
    if options.format == "csv":
        return export_csv(result)
    if options.format == "markdown":
        return export_markdown(result)
    raise ValueError(f"Unsupported format: {options.format}")
