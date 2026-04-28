"""Tests for csvdiff.entropy."""
from __future__ import annotations

import math
import pytest

from csvdiff.entropy import (
    EntropyError,
    compute_entropy,
    format_entropy,
)


@pytest.fixture()
def rows():
    return [
        {"name": "alice", "status": "active", "score": "10"},
        {"name": "bob",   "status": "active", "score": "20"},
        {"name": "carol", "status": "inactive", "score": "10"},
        {"name": "dave",  "status": "active", "score": "30"},
    ]


def test_compute_entropy_empty():
    result = compute_entropy([])
    assert result.columns == []


def test_compute_entropy_column_names(rows):
    result = compute_entropy(rows)
    names = [c.column for c in result.columns]
    assert names == ["name", "status", "score"]


def test_compute_entropy_uniform_column_is_zero(rows):
    """A column with a single repeated value should have entropy == 0."""
    uniform_rows = [{"x": "same"} for _ in range(5)]
    result = compute_entropy(uniform_rows)
    assert result.columns[0].entropy == 0.0


def test_compute_entropy_all_unique(rows):
    """'name' column has all unique values — entropy should equal log2(n)."""
    result = compute_entropy(rows, columns=["name"])
    col = result.get("name")
    assert col is not None
    expected = math.log2(4)
    assert abs(col.entropy - expected) < 1e-5


def test_compute_entropy_normalized_range(rows):
    result = compute_entropy(rows)
    for col in result.columns:
        norm = col.normalized
        if norm is not None:
            assert 0.0 <= norm <= 1.0


def test_compute_entropy_unique_values(rows):
    result = compute_entropy(rows, columns=["status"])
    col = result.get("status")
    assert col.unique_values == 2
    assert col.total_values == 4


def test_compute_entropy_subset_columns(rows):
    result = compute_entropy(rows, columns=["score"])
    assert len(result.columns) == 1
    assert result.columns[0].column == "score"


def test_compute_entropy_unknown_column_raises(rows):
    with pytest.raises(EntropyError, match="Unknown columns"):
        compute_entropy(rows, columns=["nonexistent"])


def test_get_returns_none_for_missing(rows):
    result = compute_entropy(rows)
    assert result.get("does_not_exist") is None


def test_format_entropy_empty():
    from csvdiff.entropy import EntropyResult
    text = format_entropy(EntropyResult())
    assert "No entropy data" in text


def test_format_entropy_contains_column_name(rows):
    result = compute_entropy(rows)
    text = format_entropy(result)
    assert "name" in text
    assert "status" in text
    assert "score" in text


def test_normalized_none_when_single_unique():
    single_rows = [{"x": "only"}]
    result = compute_entropy(single_rows)
    col = result.get("x")
    assert col.normalized is None
