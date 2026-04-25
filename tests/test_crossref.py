"""Tests for csvdiff.crossref."""
from __future__ import annotations

import pytest

from csvdiff.crossref import (
    CrossRefError,
    CrossRefResult,
    cross_reference,
    format_crossref,
)

LEFT = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
]

RIGHT = [
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Charlie"},
    {"id": "4", "name": "Dave"},
]


def test_cross_reference_in_both():
    result = cross_reference(LEFT, RIGHT, "id")
    assert sorted(result.in_both) == ["2", "3"]


def test_cross_reference_only_in_left():
    result = cross_reference(LEFT, RIGHT, "id")
    assert result.only_in_left == ["1"]


def test_cross_reference_only_in_right():
    result = cross_reference(LEFT, RIGHT, "id")
    assert result.only_in_right == ["4"]


def test_cross_reference_key_column_stored():
    result = cross_reference(LEFT, RIGHT, "id")
    assert result.key_column == "id"


def test_total_keys():
    result = cross_reference(LEFT, RIGHT, "id")
    assert result.total_keys == 4


def test_empty_left():
    result = cross_reference([], RIGHT, "id")
    assert result.only_in_left == []
    assert result.only_in_right == sorted(["2", "3", "4"])
    assert result.in_both == []


def test_empty_right():
    result = cross_reference(LEFT, [], "id")
    assert result.only_in_right == []
    assert result.only_in_left == sorted(["1", "2", "3"])


def test_missing_key_column_left():
    with pytest.raises(CrossRefError, match="Key column"):
        cross_reference(LEFT, RIGHT, "nonexistent")


def test_missing_key_column_right():
    with pytest.raises(CrossRefError, match="Key column"):
        cross_reference(RIGHT, LEFT, "nonexistent")


def test_empty_key_column_raises():
    with pytest.raises(CrossRefError, match="key_column"):
        cross_reference(LEFT, RIGHT, "")


def test_format_crossref_contains_key():
    result = cross_reference(LEFT, RIGHT, "id")
    text = format_crossref(result)
    assert "id" in text


def test_format_crossref_shows_counts():
    result = cross_reference(LEFT, RIGHT, "id")
    text = format_crossref(result)
    assert "2" in text  # in_both count


def test_format_crossref_lists_left_only_keys():
    result = cross_reference(LEFT, RIGHT, "id")
    text = format_crossref(result)
    assert "1" in text


def test_format_crossref_lists_right_only_keys():
    result = cross_reference(LEFT, RIGHT, "id")
    text = format_crossref(result)
    assert "4" in text
