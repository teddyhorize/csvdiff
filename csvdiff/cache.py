"""Simple file-based cache for parsed CSV data using hashing."""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional

DEFAULT_CACHE_DIR = Path(".csvdiff_cache")


class CacheError(Exception):
    pass


def _file_hash(filepath: str) -> str:
    """Compute SHA256 hash of a file's contents."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except OSError as e:
        raise CacheError(f"Cannot read file for hashing: {e}") from e
    return h.hexdigest()


def _cache_path(filepath: str, cache_dir: Path) -> Path:
    digest = _file_hash(filepath)
    return cache_dir / f"{digest}.json"


def load_cached(filepath: str, cache_dir: Path = DEFAULT_CACHE_DIR) -> Optional[list]:
    """Return cached parsed rows if available, else None."""
    path = _cache_path(filepath, cache_dir)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
    return None


def save_cached(filepath: str, rows: list, cache_dir: Path = DEFAULT_CACHE_DIR) -> None:
    """Persist parsed rows to cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = _cache_path(filepath, cache_dir)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f)
    except OSError as e:
        raise CacheError(f"Cannot write cache: {e}") from e


def clear_cache(cache_dir: Path = DEFAULT_CACHE_DIR) -> int:
    """Delete all cache files. Returns number of files removed."""
    if not cache_dir.exists():
        return 0
    count = 0
    for entry in cache_dir.glob("*.json"):
        entry.unlink()
        count += 1
    return count
