"""Bookmark support: save and restore named diff configurations."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

DEFAULT_BOOKMARK_FILE = os.path.expanduser("~/.csvdiff_bookmarks.json")


class BookmarkError(Exception):
    pass


@dataclass
class Bookmark:
    name: str
    file_a: str
    file_b: str
    key: Optional[str] = None
    delimiter: Optional[str] = None
    note: Optional[str] = None


def _load_store(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise BookmarkError(f"Corrupt bookmark file: {e}") from e


def _save_store(path: str, store: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)


def save_bookmark(bookmark: Bookmark, path: str = DEFAULT_BOOKMARK_FILE) -> None:
    store = _load_store(path)
    store[bookmark.name] = asdict(bookmark)
    _save_store(path, store)


def load_bookmark(name: str, path: str = DEFAULT_BOOKMARK_FILE) -> Bookmark:
    store = _load_store(path)
    if name not in store:
        raise BookmarkError(f"Bookmark '{name}' not found.")
    data = store[name]
    return Bookmark(**data)


def list_bookmarks(path: str = DEFAULT_BOOKMARK_FILE) -> list[Bookmark]:
    store = _load_store(path)
    return [Bookmark(**v) for v in store.values()]


def delete_bookmark(name: str, path: str = DEFAULT_BOOKMARK_FILE) -> None:
    store = _load_store(path)
    if name not in store:
        raise BookmarkError(f"Bookmark '{name}' not found.")
    del store[name]
    _save_store(path, store)


def format_bookmark(b: Bookmark) -> str:
    parts = [f"[{b.name}] {b.file_a} vs {b.file_b}"]
    if b.key:
        parts.append(f"key={b.key}")
    if b.delimiter:
        parts.append(f"delimiter={b.delimiter!r}")
    if b.note:
        parts.append(f"note: {b.note}")
    return "  ".join(parts)
