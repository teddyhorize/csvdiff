"""Clipboard integration: copy diff output to system clipboard."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


class ClipError(Exception):
    """Raised when clipboard operations fail."""


@dataclass
class ClipOptions:
    enabled: bool = False
    format: str = "text"  # "text" or "csv"


def _get_copy_command() -> list[str]:
    """Return the platform-appropriate clipboard copy command."""
    if sys.platform == "darwin":
        return ["pbcopy"]
    if sys.platform.startswith("linux"):
        return ["xclip", "-selection", "clipboard"]
    if sys.platform == "win32":
        return ["clip"]
    raise ClipError(f"Unsupported platform for clipboard: {sys.platform}")


def copy_to_clipboard(text: str) -> None:
    """Copy *text* to the system clipboard.

    Raises:
        ClipError: if the clipboard command is unavailable or fails.
    """
    if not text:
        raise ClipError("Nothing to copy: text is empty.")

    try:
        cmd = _get_copy_command()
        result = subprocess.run(
            cmd,
            input=text.encode(),
            capture_output=True,
        )
        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace").strip()
            raise ClipError(f"Clipboard command failed: {stderr}")
    except FileNotFoundError as exc:
        raise ClipError(f"Clipboard command not found: {exc}") from exc


def maybe_copy_to_clipboard(text: str, opts: Optional[ClipOptions]) -> bool:
    """Copy *text* to clipboard if *opts* requests it.

    Returns True if the copy was performed, False otherwise.
    """
    if opts is None or not opts.enabled:
        return False
    copy_to_clipboard(text)
    return True
