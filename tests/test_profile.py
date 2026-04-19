"""Tests for csvdiff.profile."""
import pytest
from csvdiff.profile import (
    profile_rows,
    format_profile,
    ColumnProfile,
    ProfileResult,
)


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob",   "score": ""},
        {"id": "3", "name": "Alice", "score": "85"},
    ]


def test_profile_empty_rows():
    result = profile_rows([])
    assert result.columns == {}


def test_profile_column_names(rows):
    result = profile_rows(rows)
    assert set(result.columns.keys()) == {"id", "name", "score"}


def test_profile_count(rows):
    result = profile_rows(rows)
    assert result.columns["id"].count == 3


def test_profile_empty_count(rows):
    result = profile_rows(rows)
    assert result.columns["score"].empty_count == 1


def test_profile_fill_rate_full(rows):
    result = profile_rows(rows)
    assert result.columns["id"].fill_rate == 1.0


def test_profile_fill_rate_partial(rows):
    result = profile_rows(rows)
    assert result.columns["score"].fill_rate == pytest.approx(2 / 3, rel=1e-3)


def test_profile_unique_values(rows):
    result = profile_rows(rows)
    assert result.columns["name"].unique_values == 2
    assert result.columns["id"].unique_values == 3


def test_profile_min_max_length(rows):
    result = profile_rows(rows)
    p = result.columns["name"]
    assert p.min_length == 3  # Bob
    assert p.max_length == 5  # Alice


def test_profile_sample_values_populated(rows):
    result = profile_rows(rows)
    assert len(result.columns["id"].sample_values) > 0


def test_profile_sample_values_no_duplicates(rows):
    result = profile_rows(rows)
    samples = result.columns["name"].sample_values
    assert len(samples) == len(set(samples))


def test_format_profile_empty():
    result = ProfileResult()
    output = format_profile(result)
    assert "No columns" in output


def test_format_profile_contains_column_name(rows):
    result = profile_rows(rows)
    output = format_profile(result)
    assert "name" in output
    assert "score" in output


def test_format_profile_shows_fill_rate(rows):
    result = profile_rows(rows)
    output = format_profile(result)
    assert "Fill rate" in output
