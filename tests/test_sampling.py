"""Tests for csvdiff.sampling."""

import pytest
from csvdiff.sampling import (
    SamplingError,
    SamplingOptions,
    sample_rows,
    sample_pair,
)


def _rows(n: int):
    return [{"id": str(i), "val": str(i * 2)} for i in range(n)]


def test_sample_n_basic():
    rows = _rows(20)
    result = sample_rows(rows, SamplingOptions(n=5, seed=0))
    assert len(result) == 5


def test_sample_n_larger_than_total_clamps():
    rows = _rows(3)
    result = sample_rows(rows, SamplingOptions(n=100, seed=0))
    assert len(result) == 3


def test_sample_fraction():
    rows = _rows(100)
    result = sample_rows(rows, SamplingOptions(fraction=0.1, seed=42))
    assert len(result) == 10


def test_sample_reproducible_with_seed():
    rows = _rows(50)
    opts = SamplingOptions(n=10, seed=7)
    assert sample_rows(rows, opts) == sample_rows(rows, opts)


def test_sample_different_seeds_differ():
    rows = _rows(50)
    a = sample_rows(rows, SamplingOptions(n=10, seed=1))
    b = sample_rows(rows, SamplingOptions(n=10, seed=2))
    assert a != b


def test_sample_systematic():
    rows = _rows(10)
    result = sample_rows(rows, SamplingOptions(n=5, systematic=True))
    assert len(result) == 5
    assert result[0] == rows[0]
    assert result[1] == rows[2]


def test_sample_empty_rows():
    assert sample_rows([], SamplingOptions(n=5)) == []


def test_sample_pair_returns_two_lists():
    a, b = sample_pair(_rows(20), _rows(30), SamplingOptions(n=5, seed=0))
    assert len(a) == 5
    assert len(b) == 5


def test_error_both_n_and_fraction():
    with pytest.raises(SamplingError, match="not both"):
        sample_rows(_rows(10), SamplingOptions(n=3, fraction=0.5))


def test_error_invalid_fraction():
    with pytest.raises(SamplingError, match="fraction"):
        sample_rows(_rows(10), SamplingOptions(fraction=1.5))


def test_error_n_zero():
    with pytest.raises(SamplingError, match="n must be"):
        sample_rows(_rows(10), SamplingOptions(n=0))
