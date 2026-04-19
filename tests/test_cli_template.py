"""Tests for csvdiff/cli_template.py"""
import argparse
import pytest
from csvdiff.differ import DiffResult
from csvdiff.cli_template import (
    register_template_args,
    template_options_from_args,
    maybe_render_template,
)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_template_args(p)
    return p


@pytest.fixture
def diff_result():
    return DiffResult(
        added=[{"id": "1", "val": "x"}],
        removed=[],
        modified=[],
        added_columns=[],
        removed_columns=[],
    )


def test_register_template_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "template")
    assert hasattr(args, "template_sep")


def test_template_options_none_when_not_set(parser):
    args = parser.parse_args([])
    assert template_options_from_args(args) is None


def test_template_options_from_args(parser):
    args = parser.parse_args(["--template", "{label}:{id}"])
    opts = template_options_from_args(args)
    assert opts is not None
    assert opts.template == "{label}:{id}"


def test_template_options_custom_sep(parser):
    args = parser.parse_args(["--template", "{label}", "--template-sep", "|"])
    opts = template_options_from_args(args)
    assert opts.separator == "|"


def test_maybe_render_template_returns_false_when_no_template(parser, diff_result):
    args = parser.parse_args([])
    assert maybe_render_template(diff_result, args) is False


def test_maybe_render_template_returns_true_when_set(parser, diff_result, capsys):
    args = parser.parse_args(["--template", "{label}:{id}"])
    result = maybe_render_template(diff_result, args)
    assert result is True
    captured = capsys.readouterr()
    assert "ADDED:1" in captured.out
