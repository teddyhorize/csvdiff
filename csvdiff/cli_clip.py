"""CLI helpers for clipboard integration."""

from __future__ import annotations

import argparse
from typing import Optional

from csvdiff.clip import ClipError, ClipOptions, maybe_copy_to_clipboard


def register_clip_args(parser: argparse.ArgumentParser) -> None:
    """Add clipboard-related arguments to *parser*."""
    group = parser.add_argument_group("clipboard")
    group.add_argument(
        "--copy",
        action="store_true",
        default=False,
        help="Copy diff output to the system clipboard.",
    )
    group.add_argument(
        "--copy-format",
        choices=["text", "csv"],
        default="text",
        dest="copy_format",
        help="Format to use when copying to clipboard (default: text).",
    )


def clip_options_from_args(args: argparse.Namespace) -> Optional[ClipOptions]:
    """Build a :class:`ClipOptions` from parsed CLI arguments.

    Returns *None* when ``--copy`` was not requested.
    """
    if not getattr(args, "copy", False):
        return None
    return ClipOptions(
        enabled=True,
        format=getattr(args, "copy_format", "text"),
    )


def handle_clip(text: str, args: argparse.Namespace) -> None:
    """Copy *text* to clipboard when requested by *args*.

    Prints a confirmation or error message to stdout/stderr.
    """
    opts = clip_options_from_args(args)
    try:
        copied = maybe_copy_to_clipboard(text, opts)
        if copied:
            print("[csvdiff] Output copied to clipboard.")
    except ClipError as exc:
        print(f"[csvdiff] Clipboard error: {exc}")
