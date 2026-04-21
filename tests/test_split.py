"""Tests for csvdiff.split."""

from __future__ import annotations

import os
import csv
import pytest

from csvdiff.differ import DiffResult
from csvdiff.split import (
    SplitOptions,
    SplitResult,
    split_diff,
    format_split_result,
    _rows_to_csv,
)


HEADERS = ["id", "name", "value"]


@pytest.fixture()
def diff_result():
    return DiffResult(
        added_rows=[{"id": "3", "name": "Charlie", "value": "30"}],
        removed_rows=[{"id": "1", "name": "Alice", "value": "10"}],
        modified_rows=[
            {
                "key": "2",
                "old": {"id": "2", "name": "Bob", "value": "20"},
                "new": {"id": "2", "name": "Bob", "value": "99"},
            }
        ],
        unchanged_rows=[{"id": "4", "name": "Dana", "value": "40"}],
    )


def test_rows_to_csv_includes_header():
    rows = [{"id": "1", "name": "Alice"}]
    result = _rows_to_csv(rows, ["id", "name"])
    assert result.startswith("id,name")


def test_rows_to_csv_includes_data():
    rows = [{"id": "1", "name": "Alice"}]
    result = _rows_to_csv(rows, ["id", "name"])
    assert "Alice" in result


def test_split_diff_creates_added_file(tmp_path, diff_result):
    opts = SplitOptions(output_dir=str(tmp_path))
    result = split_diff(diff_result, HEADERS, opts)
    assert result.added_path is not None
    assert os.path.isfile(result.added_path)


def test_split_diff_creates_removed_file(tmp_path, diff_result):
    opts = SplitOptions(output_dir=str(tmp_path))
    result = split_diff(diff_result, HEADERS, opts)
    assert result.removed_path is not None
    assert os.path.isfile(result.removed_path)


def test_split_diff_creates_modified_file(tmp_path, diff_result):
    opts = SplitOptions(output_dir=str(tmp_path))
    result = split_diff(diff_result, HEADERS, opts)
    assert result.modified_path is not None
    assert os.path.isfile(result.modified_path)


def test_split_diff_no_unchanged_by_default(tmp_path, diff_result):
    opts = SplitOptions(output_dir=str(tmp_path))
    result = split_diff(diff_result, HEADERS, opts)
    assert result.unchanged_path is None


def test_split_diff_include_unchanged(tmp_path, diff_result):
    opts = SplitOptions(output_dir=str(tmp_path), include_unchanged=True)
    result = split_diff(diff_result, HEADERS, opts)
    assert result.unchanged_path is not None
    assert os.path.isfile(result.unchanged_path)


def test_split_diff_prefix_applied(tmp_path, diff_result):
    opts = SplitOptions(output_dir=str(tmp_path), prefix="out")
    result = split_diff(diff_result, HEADERS, opts)
    assert "out_added" in result.added_path


def test_split_diff_files_written_list(tmp_path, diff_result):
    opts = SplitOptions(output_dir=str(tmp_path))
    result = split_diff(diff_result, HEADERS, opts)
    assert len(result.files_written) == 3


def test_split_diff_no_differences_empty(tmp_path):
    empty = DiffResult(added_rows=[], removed_rows=[], modified_rows=[], unchanged_rows=[])
    opts = SplitOptions(output_dir=str(tmp_path))
    result = split_diff(empty, HEADERS, opts)
    assert result.files_written == []


def test_format_split_result_no_files():
    r = SplitResult()
    msg = format_split_result(r)
    assert "No files" in msg


def test_format_split_result_with_files():
    r = SplitResult(files_written=["/tmp/diff_added.csv", "/tmp/diff_removed.csv"])
    msg = format_split_result(r)
    assert "diff_added.csv" in msg
    assert "diff_removed.csv" in msg
