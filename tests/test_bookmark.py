"""Tests for csvdiff.bookmark."""

import pytest
from csvdiff.bookmark import (
    Bookmark,
    BookmarkError,
    save_bookmark,
    load_bookmark,
    list_bookmarks,
    delete_bookmark,
    format_bookmark,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "bookmarks.json")


def _bm(**kwargs):
    defaults = {"name": "test", "file_a": "a.csv", "file_b": "b.csv"}
    defaults.update(kwargs)
    return Bookmark(**defaults)


def test_save_and_load(store):
    bm = _bm(name="mytest", key="id")
    save_bookmark(bm, store)
    result = load_bookmark("mytest", store)
    assert result.name == "mytest"
    assert result.file_a == "a.csv"
    assert result.key == "id"


def test_load_missing_raises(store):
    with pytest.raises(BookmarkError, match="not found"):
        load_bookmark("ghost", store)


def test_list_empty(store):
    assert list_bookmarks(store) == []


def test_list_multiple(store):
    save_bookmark(_bm(name="alpha"), store)
    save_bookmark(_bm(name="beta"), store)
    names = {b.name for b in list_bookmarks(store)}
    assert names == {"alpha", "beta"}


def test_delete(store):
    save_bookmark(_bm(name="todel"), store)
    delete_bookmark("todel", store)
    with pytest.raises(BookmarkError):
        load_bookmark("todel", store)


def test_delete_missing_raises(store):
    with pytest.raises(BookmarkError, match="not found"):
        delete_bookmark("nope", store)


def test_overwrite_bookmark(store):
    save_bookmark(_bm(name="dup", key="id"), store)
    save_bookmark(_bm(name="dup", key="uuid"), store)
    result = load_bookmark("dup", store)
    assert result.key == "uuid"


def test_format_basic():
    bm = _bm(name="x")
    out = format_bookmark(bm)
    assert "a.csv" in out and "b.csv" in out and "[x]" in out


def test_format_with_extras():
    bm = _bm(name="x", key="id", delimiter=";", note="important")
    out = format_bookmark(bm)
    assert "key=id" in out
    assert "note: important" in out


def test_corrupt_store(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not json")
    with pytest.raises(BookmarkError, match="Corrupt"):
        list_bookmarks(str(p))
