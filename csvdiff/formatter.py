"""Formatting utilities for rendering diff results to the terminal."""

from dataclasses import dataclass
from typing import Optional
from csvdiff.differ import DiffResult

ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


@dataclass
class FormatOptions:
    color: bool = True
    show_summary: bool = True
    compact: bool = False


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_diff(result: DiffResult, options: Optional[FormatOptions] = None) -> str:
    if options is None:
        options = FormatOptions()

    lines = []

    if result.added_rows:
        header = _colorize(f"+ Added rows ({len(result.added_rows)}):", ANSI_GREEN, options.color)
        lines.append(header)
        if not options.compact:
            for key, row in result.added_rows.items():
                lines.append(_colorize(f"  + {key}: {row}", ANSI_GREEN, options.color))

    if result.removed_rows:
        header = _colorize(f"- Removed rows ({len(result.removed_rows)}):", ANSI_RED, options.color)
        lines.append(header)
        if not options.compact:
            for key, row in result.removed_rows.items():
                lines.append(_colorize(f"  - {key}: {row}", ANSI_RED, options.color))

    if result.modified_rows:
        header = _colorize(f"~ Modified rows ({len(result.modified_rows)}):", ANSI_YELLOW, options.color)
        lines.append(header)
        if not options.compact:
            for key, changes in result.modified_rows.items():
                lines.append(_colorize(f"  ~ {key}:", ANSI_YELLOW, options.color))
                for field, (old_val, new_val) in changes.items():
                    lines.append(_colorize(f"      {field}: {old_val!r} -> {new_val!r}", ANSI_YELLOW, options.color))

    if result.added_columns:
        lines.append(_colorize(f"+ Added columns: {result.added_columns}", ANSI_GREEN, options.color))

    if result.removed_columns:
        lines.append(_colorize(f"- Removed columns: {result.removed_columns}", ANSI_RED, options.color))

    if options.show_summary:
        lines.append("")
        summary = (
            f"Summary: {len(result.added_rows)} added, "
            f"{len(result.removed_rows)} removed, "
            f"{len(result.modified_rows)} modified"
        )
        lines.append(_colorize(summary, ANSI_BOLD, options.color))

    if not lines or (options.show_summary and len(lines) <= 2):
        return _colorize("No differences found.", ANSI_BOLD, options.color)

    return "\n".join(lines)
