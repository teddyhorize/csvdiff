"""Tests for csvdiff.fingerprint and csvdiff.cli_fingerprint."""
from __future__ import annotations

import argparse
import json

import pytest

from csvdiff.differ import DiffResult
from csvdiff.fingerprint import (
    FingerprintError,
    Fingerprint,
    _hash_rows,
    _hash_diff,
    compute_fingerprint,
    format_fingerprint,
)
from csvdiff.cli_fingerprint import (
    register_fingerprint_args,
    fingerprint_as_dict,
    maybe_print_fingerprint,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

LEFT = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
RIGHT = [{"id": "1", "name": "Alice"}, {"id": "3", "name": "Carol"}]


@pytest.fixture
def empty_diff() -> DiffResult:
    return DiffResult(added_rows=[], removed_rows=[], modified_rows=[], added_columns=[], removed_columns=[])


@pytest.fixture
def full_diff() -> DiffResult:
    return DiffResult(
        added_rows=[{"id": "3", "name": "Carol"}],
        removed_rows=[{"id": "2", "name": "Bob"}],
        modified_rows=[("1", {"id": "1", "name": "Alice"}, {"id": "1", "name": "Alicia"})],
        added_columns=[],
        removed_columns=[],
    )


# ---------------------------------------------------------------------------
# _hash_rows
# ---------------------------------------------------------------------------

def test_hash_rows_returns_string():
    assert isinstance(_hash_rows(LEFT), str)


def test_hash_rows_deterministic():
    assert _hash_rows(LEFT) == _hash_rows(LEFT)


def test_hash_rows_differs_on_different_data():
    assert _hash_rows(LEFT) != _hash_rows(RIGHT)


def test_hash_rows_empty_list():
    h = _hash_rows([])
    assert len(h) == 64  # SHA-256 hex length


# ---------------------------------------------------------------------------
# compute_fingerprint
# ---------------------------------------------------------------------------

def test_compute_fingerprint_returns_fingerprint(empty_diff):
    fp = compute_fingerprint(LEFT, LEFT, empty_diff)
    assert isinstance(fp, Fingerprint)


def test_compute_fingerprint_identical(empty_diff):
    fp = compute_fingerprint(LEFT, LEFT, empty_diff)
    assert fp.is_identical is True


def test_compute_fingerprint_not_identical(full_diff):
    fp = compute_fingerprint(LEFT, RIGHT, full_diff)
    assert fp.is_identical is False


def test_compute_fingerprint_row_counts(empty_diff):
    fp = compute_fingerprint(LEFT, RIGHT, empty_diff)
    assert fp.row_count_left == 2
    assert fp.row_count_right == 2


def test_compute_fingerprint_none_raises(empty_diff):
    with pytest.raises(FingerprintError):
        compute_fingerprint(None, RIGHT, empty_diff)


# ---------------------------------------------------------------------------
# format_fingerprint
# ---------------------------------------------------------------------------

def test_format_fingerprint_contains_status(empty_diff):
    fp = compute_fingerprint(LEFT, LEFT, empty_diff)
    text = format_fingerprint(fp)
    assert "identical" in text


def test_format_fingerprint_changed(full_diff):
    fp = compute_fingerprint(LEFT, RIGHT, full_diff)
    text = format_fingerprint(fp)
    assert "changed" in text


# ---------------------------------------------------------------------------
# cli helpers
# ---------------------------------------------------------------------------

def test_register_fingerprint_args():
    parser = argparse.ArgumentParser()
    register_fingerprint_args(parser)
    args = parser.parse_args([])
    assert args.fingerprint is False
    assert args.fingerprint_json is False


def test_fingerprint_as_dict_keys(empty_diff):
    fp = compute_fingerprint(LEFT, LEFT, empty_diff)
    d = fingerprint_as_dict(fp)
    assert set(d.keys()) == {"left_hash", "right_hash", "diff_hash", "row_count_left", "row_count_right", "is_identical"}


def test_maybe_print_fingerprint_skipped_when_not_set(empty_diff, capsys):
    parser = argparse.ArgumentParser()
    register_fingerprint_args(parser)
    args = parser.parse_args([])
    result = maybe_print_fingerprint(args, LEFT, LEFT, empty_diff)
    assert result is None
    assert capsys.readouterr().out == ""


def test_maybe_print_fingerprint_prints(empty_diff, capsys):
    parser = argparse.ArgumentParser()
    register_fingerprint_args(parser)
    args = parser.parse_args(["--fingerprint"])
    fp = maybe_print_fingerprint(args, LEFT, LEFT, empty_diff)
    assert fp is not None
    out = capsys.readouterr().out
    assert "identical" in out


def test_maybe_print_fingerprint_json(empty_diff, capsys):
    parser = argparse.ArgumentParser()
    register_fingerprint_args(parser)
    args = parser.parse_args(["--fingerprint", "--fingerprint-json"])
    maybe_print_fingerprint(args, LEFT, RIGHT, empty_diff)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "left_hash" in data
