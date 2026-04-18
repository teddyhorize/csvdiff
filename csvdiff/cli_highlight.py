"""CLI helpers for cell-level highlight output."""
import argparse
from typing import Optional

from csvdiff.highlight import highlight_modified, format_highlight
from csvdiff.differ import DiffResult


def register_highlight_args(parser: argparse.ArgumentParser) -> None:
    """Add highlight-related flags to an argument parser."""
    parser.add_argument(
        "--highlight",
        action="store_true",
        default=False,
        help="Show cell-level diff for modified rows.",
    )
    parser.add_argument(
        "--no-color",
        dest="no_color",
        action="store_true",
        default=False,
        help="Disable ANSI color in highlight output.",
    )


def print_highlights(
    diff: DiffResult,
    use_color: bool = True,
    out=None,
) -> None:
    """Print cell-level highlights for a DiffResult to *out* (default stdout)."""
    import sys

    out = out or sys.stdout
    highlights = highlight_modified(diff.modified)
    text = format_highlight(highlights, use_color=use_color)
    out.write(text + "\n")


def maybe_print_highlights(
    args: argparse.Namespace,
    diff: DiffResult,
    out=None,
) -> None:
    """Conditionally print highlights based on parsed CLI args."""
    if getattr(args, "highlight", False):
        use_color = not getattr(args, "no_color", False)
        print_highlights(diff, use_color=use_color, out=out)
