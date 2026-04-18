"""Tests for csvdiff.cache module."""

import json
import pytest
from pathlib import Path
from csvdiff.cache import (
    CacheError,
    _file_hash,
    load_cached,
    save_cached,
    clear_cache,
)


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "sample.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n")
    return str(p)


@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path / "cache"


def test_file_hash_returns_string(sample_csv):
    digest = _file_hash(sample_csv)
    assert isinstance(digest, str)
    assert len(digest) == 64


def test_file_hash_deterministic(sample_csv):
    assert _file_hash(sample_csv) == _file_hash(sample_csv)


def test_file_hash_changes_with_content(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id\n1\n")
    b.write_text("id\n2\n")
    assert _file_hash(str(a)) != _file_hash(str(b))


def test_file_hash_missing_file():
    with pytest.raises(CacheError):
        _file_hash("/nonexistent/file.csv")


def test_load_cached_miss(sample_csv, cache_dir):
    assert load_cached(sample_csv, cache_dir) is None


def test_save_and_load_cached(sample_csv, cache_dir):
    rows = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    save_cached(sample_csv, rows, cache_dir)
    result = load_cached(sample_csv, cache_dir)
    assert result == rows


def test_cache_dir_created(sample_csv, cache_dir):
    assert not cache_dir.exists()
    save_cached(sample_csv, [], cache_dir)
    assert cache_dir.exists()


def test_clear_cache(sample_csv, cache_dir):
    save_cached(sample_csv, [{"id": "1"}], cache_dir)
    removed = clear_cache(cache_dir)
    assert removed == 1
    assert load_cached(sample_csv, cache_dir) is None


def test_clear_cache_nonexistent_dir(tmp_path):
    missing = tmp_path / "no_cache"
    assert clear_cache(missing) == 0
