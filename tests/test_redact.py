"""Tests for csvdiff.redact."""

import pytest
from csvdiff.redact import (
    RedactError,
    RedactOptions,
    redact_row,
    redact_rows,
    redact_pair,
)


@pytest.fixture()
def row():
    return {"name": "Alice", "email": "alice@example.com", "score": "42"}


def test_redact_row_no_columns(row):
    opts = RedactOptions(columns=[])
    result = redact_row(row, opts)
    assert result == row


def test_redact_row_single_column(row):
    opts = RedactOptions(columns=["email"])
    result = redact_row(row, opts)
    assert result["email"] == "***"
    assert result["name"] == "Alice"
    assert result["score"] == "42"


def test_redact_row_multiple_columns(row):
    opts = RedactOptions(columns=["email", "score"])
    result = redact_row(row, opts)
    assert result["email"] == "***"
    assert result["score"] == "***"
    assert result["name"] == "Alice"


def test_redact_row_custom_placeholder(row):
    opts = RedactOptions(columns=["email"], placeholder="[REDACTED]")
    result = redact_row(row, opts)
    assert result["email"] == "[REDACTED]"


def test_redact_row_does_not_mutate_original(row):
    original_email = row["email"]
    opts = RedactOptions(columns=["email"])
    redact_row(row, opts)
    assert row["email"] == original_email


def test_redact_row_unknown_column_ignored(row):
    opts = RedactOptions(columns=["nonexistent"])
    result = redact_row(row, opts)
    assert result == row


def test_redact_rows_applies_to_all(row):
    rows = [row, {"name": "Bob", "email": "bob@example.com", "score": "7"}]
    opts = RedactOptions(columns=["email"])
    results = redact_rows(rows, opts)
    assert all(r["email"] == "***" for r in results)
    assert results[0]["name"] == "Alice"
    assert results[1]["name"] == "Bob"


def test_redact_rows_empty_list():
    opts = RedactOptions(columns=["email"])
    assert redact_rows([], opts) == []


def test_redact_pair_redacts_both_sides():
    left = [{"id": "1", "secret": "abc"}]
    right = [{"id": "1", "secret": "xyz"}]
    opts = RedactOptions(columns=["secret"])
    l_out, r_out = redact_pair(left, right, opts)
    assert l_out[0]["secret"] == "***"
    assert r_out[0]["secret"] == "***"


def test_redact_empty_placeholder_raises(row):
    opts = RedactOptions(columns=["email"], placeholder="")
    with pytest.raises(RedactError):
        redact_row(row, opts)
