"""Tests for csvdiff.cli_patch module."""

import json
import argparse
import pytest
from csvdiff.cli_patch import (
    register_patch_args, patch_to_dict, patch_from_dict, maybe_print_patch
)
from csvdiff.patch import Patch, PatchOperation
from csvdiff.differ import DiffResult


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_patch_args(p)
    return p


@pytest.fixture
def sample_patch():
    return Patch(
        key_column="id",
        operations=[
            PatchOperation(op="add", key="5", row={"id": "5", "val": "x"}),
            PatchOperation(op="remove", key="2", row={"id": "2", "val": "y"}),
        ]
    )


def test_register_patch_args(parser):
    args = parser.parse_args(["--patch"])
    assert args.patch is True


def test_register_patch_output_arg(parser):
    args = parser.parse_args(["--patch-output", "out.json"])
    assert args.patch_output == "out.json"


def test_patch_to_dict_structure(sample_patch):
    d = patch_to_dict(sample_patch)
    assert d["key_column"] == "id"
    assert len(d["operations"]) == 2
    assert d["operations"][0]["op"] == "add"


def test_patch_roundtrip(sample_patch):
    d = patch_to_dict(sample_patch)
    restored = patch_from_dict(d)
    assert restored.key_column == sample_patch.key_column
    assert len(restored.operations) == len(sample_patch.operations)


def test_maybe_print_patch_false_when_no_flag(capsys):
    diff = DiffResult({}, {}, {}, [], [])
    args = argparse.Namespace(patch=False)
    result = maybe_print_patch(diff, "id", args)
    assert result is False


def test_maybe_print_patch_true_when_flag(capsys):
    diff = DiffResult(
        added_rows={"1": {"id": "1"}}, removed_rows={}, modified_rows={}, added_columns=[], removed_columns=[]
    )
    args = argparse.Namespace(patch=True, patch_output=None)
    result = maybe_print_patch(diff, "id", args)
    assert result is True
    captured = capsys.readouterr()
    data = json.loads(captured.out.split("\nPatch:")[0])
    assert data["key_column"] == "id"
