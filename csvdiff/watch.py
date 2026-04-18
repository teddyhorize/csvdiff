"""File watching support for csvdiff — re-run diff when files change."""

import time
import os
from dataclasses import dataclass
from typing import Callable, Optional


class WatchError(Exception):
    pass


@dataclass
class WatchOptions:
    interval: float = 1.0
    max_iterations: Optional[int] = None  # None = run forever


def _mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)
    except OSError as e:
        raise WatchError(f"Cannot stat file '{path}': {e}") from e


def watch_files(
    paths: list[str],
    callback: Callable[[list[str]], None],
    options: Optional[WatchOptions] = None,
) -> None:
    """Watch paths for modifications and invoke callback with changed files.

    The callback receives the list of paths that changed since last check.
    Runs until max_iterations is reached (or forever if None).
    """
    if options is None:
        options = WatchOptions()

    if not paths:
        raise WatchError("No paths provided to watch.")

    mtimes = {p: _mtime(p) for p in paths}
    iterations = 0

    while True:
        if options.max_iterations is not None and iterations >= options.max_iterations:
            break

        time.sleep(options.interval)
        changed = []

        for p in paths:
            current = _mtime(p)
            if current != mtimes[p]:
                mtimes[p] = current
                changed.append(p)

        if changed:
            callback(changed)

        iterations += 1
