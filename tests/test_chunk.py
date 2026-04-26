"""Tests for csvdiff.chunk."""
import pytest

from csvdiff.chunk import (
    Chunk,
    ChunkError,
    ChunkOptions,
    chunk_diff,
    format_chunk,
)
from csvdiff.differ import DiffResult


@pytest.fixture()
def empty_result():
    return DiffResult(
        added=[], removed=[], modified=[], unchanged=[],
        added_columns=[], removed_columns=[]
    )


@pytest.fixture()
def full_result():
    return DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[{"id": "3", "name": "Carol"}],
        unchanged=[{"id": "4", "name": "Dave"}],
        added_columns=[],
        removed_columns=[],
    )


def test_chunk_empty_result_yields_one_chunk(empty_result):
    chunks = list(chunk_diff(empty_result))
    assert len(chunks) == 1
    assert chunks[0].change_count == 0


def test_chunk_default_options(full_result):
    chunks = list(chunk_diff(full_result))
    assert len(chunks) == 1
    assert chunks[0].change_count == 3


def test_chunk_does_not_include_unchanged_by_default(full_result):
    chunks = list(chunk_diff(full_result))
    assert chunks[0].unchanged == []


def test_chunk_includes_unchanged_when_opted_in(full_result):
    opts = ChunkOptions(include_unchanged=True)
    chunks = list(chunk_diff(full_result, opts))
    assert len(chunks[0].unchanged) == 1


def test_chunk_size_splits_rows():
    result = DiffResult(
        added=[{"id": str(i)} for i in range(5)],
        removed=[], modified=[], unchanged=[],
        added_columns=[], removed_columns=[],
    )
    opts = ChunkOptions(size=2)
    chunks = list(chunk_diff(result, opts))
    assert len(chunks) == 3  # ceil(5/2)
    assert chunks[-1].is_last


def test_chunk_invalid_size_raises(full_result):
    with pytest.raises(ChunkError):
        list(chunk_diff(full_result, ChunkOptions(size=0)))


def test_chunk_index_and_total(full_result):
    result = DiffResult(
        added=[{"id": str(i)} for i in range(4)],
        removed=[], modified=[], unchanged=[],
        added_columns=[], removed_columns=[],
    )
    opts = ChunkOptions(size=2)
    chunks = list(chunk_diff(result, opts))
    assert chunks[0].index == 0
    assert chunks[0].total == 2
    assert chunks[1].index == 1


def test_chunk_change_count_property():
    chunk = Chunk(index=0, total=1)
    chunk.added = [{"id": "1"}]
    chunk.removed = [{"id": "2"}, {"id": "3"}]
    assert chunk.change_count == 3


def test_is_last_true_for_single_chunk(empty_result):
    chunks = list(chunk_diff(empty_result))
    assert chunks[0].is_last


def test_format_chunk_contains_index(full_result):
    chunk = next(chunk_diff(full_result))
    text = format_chunk(chunk)
    assert "Chunk 1/1" in text


def test_format_chunk_shows_added_prefix(full_result):
    chunk = next(chunk_diff(full_result))
    text = format_chunk(chunk)
    assert "  + " in text


def test_format_chunk_shows_removed_prefix(full_result):
    chunk = next(chunk_diff(full_result))
    text = format_chunk(chunk)
    assert "  - " in text


def test_format_chunk_shows_modified_prefix(full_result):
    chunk = next(chunk_diff(full_result))
    text = format_chunk(chunk)
    assert "  ~ " in text
