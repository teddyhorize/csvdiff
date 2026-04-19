"""Tests for csvdiff.transform and csvdiff.cli_transform."""
import argparse
import pytest

from csvdiff.transform import (
    TransformError,
    TransformOptions,
    TransformRule,
    transform_row,
    transform_rows,
    transform_pair,
)
from csvdiff.cli_transform import (
    register_transform_args,
    transform_options_from_args,
    _parse_spec,
)


@pytest.fixture()
def rows():
    return [
        {"id": "1", "name": "Alice", "status": "active"},
        {"id": "2", "name": "Bob",   "status": "inactive"},
    ]


def test_transform_row_plain(rows):
    rule = TransformRule(column="status", pattern="inactive", replacement="disabled")
    result = transform_row(rows[1], TransformOptions(rules=[rule]))
    assert result["status"] == "disabled"


def test_transform_row_no_match_unchanged(rows):
    rule = TransformRule(column="status", pattern="missing", replacement="x")
    result = transform_row(rows[0], TransformOptions(rules=[rule]))
    assert result["status"] == "active"


def test_transform_row_skips_missing_column(rows):
    rule = TransformRule(column="nonexistent", pattern="a", replacement="b")
    result = transform_row(rows[0], TransformOptions(rules=[rule]))
    assert result == rows[0]


def test_transform_row_regex(rows):
    rule = TransformRule(column="name", pattern=r"^A", replacement="@", use_regex=True)
    result = transform_row(rows[0], TransformOptions(rules=[rule]))
    assert result["name"] == "@lice"


def test_invalid_regex_raises():
    with pytest.raises(TransformError):
        TransformRule(column="x", pattern="[invalid", replacement="y", use_regex=True)


def test_transform_rows_empty_rules(rows):
    opts = TransformOptions()
    assert transform_rows(rows, opts) is rows


def test_transform_rows_applies_to_all(rows):
    rule = TransformRule(column="status", pattern="active", replacement="on")
    result = transform_rows(rows, TransformOptions(rules=[rule]))
    assert result[0]["status"] == "on"
    assert result[1]["status"] == "inon"  # "inactive" -> "inon"


def test_transform_pair(rows):
    rule = TransformRule(column="id", pattern="1", replacement="one")
    opts = TransformOptions(rules=[rule])
    left, right = transform_pair(rows[:1], rows[1:], opts)
    assert left[0]["id"] == "one"
    assert right[0]["id"] == "2"


def test_register_transform_args():
    parser = argparse.ArgumentParser()
    register_transform_args(parser)
    args = parser.parse_args(["--transform", "name:Alice:Bob"])
    assert args.transform == ["name:Alice:Bob"]


def test_parse_spec_plain():
    rule = _parse_spec("col:old:new", use_regex=False)
    assert rule.column == "col"
    assert rule.pattern == "old"
    assert rule.replacement == "new"
    assert not rule.use_regex


def test_parse_spec_invalid_raises():
    with pytest.raises(TransformError):
        _parse_spec("col:only_two_parts", use_regex=False)


def test_transform_options_from_args():
    parser = argparse.ArgumentParser()
    register_transform_args(parser)
    args = parser.parse_args(["--transform", "status:active:on", "--transform-regex", r"name:^A:@"])
    opts = transform_options_from_args(args)
    assert len(opts.rules) == 2
    assert opts.rules[0].use_regex is False
    assert opts.rules[1].use_regex is True
