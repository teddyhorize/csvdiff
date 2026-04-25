"""Tests for csvdiff.mask."""
import argparse
import pytest

from csvdiff.mask import (
    MaskError,
    MaskOptions,
    mask_value,
    mask_row,
    mask_rows,
)
from csvdiff.cli_mask import (
    register_mask_args,
    mask_options_from_args,
    maybe_apply_mask,
)


@pytest.fixture
def row():
    return {"name": "Alice", "email": "alice@example.com", "age": "30"}


def test_mask_value_full(row):
    opts = MaskOptions(columns=["email"])
    assert mask_value("alice@example.com", opts) == "***"


def test_mask_value_keep_start():
    opts = MaskOptions(columns=["email"], keep_start=3)
    assert mask_value("alice@example.com", opts) == "ali***"


def test_mask_value_keep_end():
    opts = MaskOptions(columns=["email"], keep_end=4)
    assert mask_value("alice@example.com", opts) == "***.com"


def test_mask_value_keep_start_and_end():
    opts = MaskOptions(columns=["email"], keep_start=2, keep_end=3)
    assert mask_value("alice@example.com", opts) == "al***.com"


def test_mask_value_short_string_keep_start_clamps():
    opts = MaskOptions(columns=["x"], keep_start=10)
    assert mask_value("hi", opts) == "hi"


def test_mask_value_custom_placeholder():
    opts = MaskOptions(columns=["x"], placeholder="[REDACTED]")
    assert mask_value("secret", opts) == "[REDACTED]"


def test_mask_row_masks_specified_column(row):
    opts = MaskOptions(columns=["email"])
    result = mask_row(row, opts)
    assert result["email"] == "***"
    assert result["name"] == "Alice"
    assert result["age"] == "30"


def test_mask_row_ignores_missing_column(row):
    opts = MaskOptions(columns=["nonexistent"])
    result = mask_row(row, opts)
    assert result == row


def test_mask_row_does_not_mutate_original(row):
    opts = MaskOptions(columns=["email"])
    mask_row(row, opts)
    assert row["email"] == "alice@example.com"


def test_mask_rows_applies_to_all(row):
    rows = [dict(row), dict(row)]
    opts = MaskOptions(columns=["email"])
    result = mask_rows(rows, opts)
    assert all(r["email"] == "***" for r in result)


def test_mask_rows_no_opts_returns_original(row):
    rows = [row]
    assert mask_rows(rows, None) is rows


def test_mask_rows_empty_columns_returns_original(row):
    rows = [row]
    opts = MaskOptions(columns=[])
    assert mask_rows(rows, opts) is rows


def test_validate_negative_keep_start_raises():
    opts = MaskOptions(columns=["x"], keep_start=-1)
    with pytest.raises(MaskError):
        mask_value("hello", opts)


def test_validate_empty_placeholder_raises():
    opts = MaskOptions(columns=["x"], placeholder="")
    with pytest.raises(MaskError):
        mask_value("hello", opts)


# --- CLI helpers ---


def _make_parser():
    p = argparse.ArgumentParser()
    register_mask_args(p)
    return p


def test_register_mask_args_adds_flag():
    p = _make_parser()
    args = p.parse_args(["--mask", "email"])
    assert args.mask_columns == ["email"]


def test_mask_options_from_args_none_when_no_columns():
    p = _make_parser()
    args = p.parse_args([])
    assert mask_options_from_args(args) is None


def test_mask_options_from_args_builds_options():
    p = _make_parser()
    args = p.parse_args(["--mask", "email", "--mask-keep-start", "2"])
    opts = mask_options_from_args(args)
    assert opts is not None
    assert opts.columns == ["email"]
    assert opts.keep_start == 2


def test_maybe_apply_mask_no_columns_returns_unchanged(row):
    p = _make_parser()
    args = p.parse_args([])
    rows = [row]
    assert maybe_apply_mask(rows, args) is rows


def test_maybe_apply_mask_applies(row):
    p = _make_parser()
    args = p.parse_args(["--mask", "email"])
    result = maybe_apply_mask([row], args)
    assert result[0]["email"] == "***"
