"""Chunk large CSV diffs into smaller batches for processing or output."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List

from csvdiff.differ import DiffResult


class ChunkError(Exception):
    """Raised when chunking options are invalid."""


@dataclass
class ChunkOptions:
    size: int = 100
    include_unchanged: bool = False


@dataclass
class Chunk:
    index: int
    total: int
    added: List[dict] = field(default_factory=list)
    removed: List[dict] = field(default_factory=list)
    modified: List[dict] = field(default_factory=list)
    unchanged: List[dict] = field(default_factory=list)

    @property
    def is_last(self) -> bool:
        return self.index == self.total - 1

    @property
    def change_count(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)


def _validate(opts: ChunkOptions) -> None:
    if opts.size < 1:
        raise ChunkError(f"Chunk size must be >= 1, got {opts.size}")


def _all_rows(result: DiffResult, include_unchanged: bool) -> List[dict]:
    rows: List[dict] = []
    rows.extend({"_change": "added", **r} for r in result.added)
    rows.extend({"_change": "removed", **r} for r in result.removed)
    rows.extend({"_change": "modified", **r} for r in result.modified)
    if include_unchanged:
        rows.extend({"_change": "unchanged", **r} for r in result.unchanged)
    return rows


def chunk_diff(result: DiffResult, opts: ChunkOptions | None = None) -> Iterator[Chunk]:
    """Yield Chunk objects slicing the diff into batches of `opts.size` rows."""
    if opts is None:
        opts = ChunkOptions()
    _validate(opts)

    rows = _all_rows(result, opts.include_unchanged)
    total_chunks = max(1, (len(rows) + opts.size - 1) // opts.size)

    for idx in range(total_chunks):
        batch = rows[idx * opts.size : (idx + 1) * opts.size]
        chunk = Chunk(index=idx, total=total_chunks)
        for row in batch:
            tag = row.get("_change")
            clean = {k: v for k, v in row.items() if k != "_change"}
            if tag == "added":
                chunk.added.append(clean)
            elif tag == "removed":
                chunk.removed.append(clean)
            elif tag == "modified":
                chunk.modified.append(clean)
            else:
                chunk.unchanged.append(clean)
        yield chunk


def format_chunk(chunk: Chunk) -> str:
    lines = [f"Chunk {chunk.index + 1}/{chunk.total} — {chunk.change_count} change(s)"]
    for r in chunk.added:
        lines.append(f"  + {r}")
    for r in chunk.removed:
        lines.append(f"  - {r}")
    for r in chunk.modified:
        lines.append(f"  ~ {r}")
    return "\n".join(lines)
