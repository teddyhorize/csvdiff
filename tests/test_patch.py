"""Tests for csvdiff.patch module."""

import pytest
from csvdiff.patch import (
    build_patch, apply_patch, patch_summary, Patch, PatchOperation, PatchError
)
from csvdiff.differ import DiffResult


@pytest.fixture
def base_rows():
    return [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
        {"id": "3", "name": "Carol", "age": "28"},
    ]


@pytest.fixture
def diff_result():
    return DiffResult(
        added_rows={"4": {"id": "4", "name": "Dave", "age": "22"}},
        removed_rows={"3": {"id": "3", "name": "Carol", "age": "28"}},
        modified_rows={"1": {"age": {"old": "30", "new": "31"}}},
        added_columns=[],
        removed_columns=[],
    )


def test_build_patch_operations(diff_result):
    patch = build_patch(diff_result, "id")
    ops = {op.op for op in patch.operations}
    assert "add" in ops
    assert "remove" in ops
    assert "modify" in ops


def test_build_patch_key_column(diff_result):
    patch = build_patch(diff_result, "id")
    assert patch.key_column == "id"


def test_build_patch_is_empty():
    empty = DiffResult({}, {}, {}, [], [])
    patch = build_patch(empty, "id")
    assert patch.is_empty()


def test_apply_patch_add(base_rows):
    patch = Patch(key_column="id", operations=[
        PatchOperation(op="add", key="4", row={"id": "4", "name": "Dave", "age": "22"})
    ])
    result = apply_patch(base_rows, patch)
    keys = [r["id"] for r in result]
    assert "4" in keys


def test_apply_patch_remove(base_rows):
    patch = Patch(key_column="id", operations=[
        PatchOperation(op="remove", key="2", row={})
    ])
    result = apply_patch(base_rows, patch)
    keys = [r["id"] for r in result]
    assert "2" not in keys


def test_apply_patch_modify(base_rows):
    patch = Patch(key_column="id", operations=[
        PatchOperation(op="modify", key="1", changes={"age": {"old": "30", "new": "31"}})
    ])
    result = apply_patch(base_rows, patch)
    row = next(r for r in result if r["id"] == "1")
    assert row["age"] == "31"


def test_apply_patch_add_duplicate_raises(base_rows):
    patch = Patch(key_column="id", operations=[
        PatchOperation(op="add", key="1", row={"id": "1", "name": "X", "age": "0"})
    ])
    with pytest.raises(PatchError):
        apply_patch(base_rows, patch)


def test_apply_patch_remove_missing_raises(base_rows):
    patch = Patch(key_column="id", operations=[
        PatchOperation(op="remove", key="99", row={})
    ])
    with pytest.raises(PatchError):
        apply_patch(base_rows, patch)


def test_apply_patch_unknown_op_raises(base_rows):
    patch = Patch(key_column="id", operations=[
        PatchOperation(op="upsert", key="1")
    ])
    with pytest.raises(PatchError):
        apply_patch(base_rows, patch)


def test_patch_summary(diff_result):
    patch = build_patch(diff_result, "id")
    summary = patch_summary(patch)
    assert "1 additions" in summary
    assert "1 removals" in summary
    assert "1 modifications" in summary
