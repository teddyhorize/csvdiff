"""Tests for csvdiff.cli_profile."""
import argparse
import jsonfrom io import StringIO
from unittest.mock import patch

import pytest

from csvdiff.cli_profile import (
    register_profile_args,
    profile_as_dict,
    maybe_print_profiles,nfrom csvdiff.profile import profile_rows


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_profile_args(p)
    return p


@pytest.fixture
def rows():
    return [
        {"id": "1", "city": "London"},
        {"id": "2", "city": "Paris"},
    ]


def test_register_profile_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "profile")
    assert args.profile is False


def test_register_profile_json_arg(parser):
    args = parser.parse_args(["--profile-json"])
    assert args.profile_json is True


def test_profile_as_dict_keys(rows):
    result = profile_rows(rows)
    d = profile_as_dict(result)
    assert "id" in d
    assert "city" in d


def test_profile_as_dict_fields(rows):
    result = profile_rows(rows)
    d = profile_as_dict(result)
    col = d["id"]
    assert "count" in col
    assert "fill_rate" in col
    assert "unique_values" in col
    assert "sample_values" in col


def test_maybe_print_profiles_skipped_when_not_set(rows, capsys):
    args = argparse.Namespace(profile=False, profile_json=False)
    maybe_print_profiles(args, rows, rows)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_maybe_print_profiles_text_output(rows, capsys):
    args = argparse.Namespace(profile=True, profile_json=False)
    maybe_print_profiles(args, rows, rows)
    captured = capsys.readouterr()
    assert "FILE1" in captured.out
    assert "FILE2" in captured.out
    assert "Fill rate" in captured.out


def test_maybe_print_profiles_json_output(rows, capsys):
    args = argparse.Namespace(profile=True, profile_json=True)
    maybe_print_profiles(args, rows, rows)
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert "FILE1" in data or "FILE2" in data
