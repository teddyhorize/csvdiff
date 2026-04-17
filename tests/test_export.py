"""Tests for csvdiff.export module."""

import json
import pytest

from csvdiff.differ import DiffResult
from csvdiff.export import ExportOptions, export_diff, export_json, export_csv, export_markdown


@pytest.fixture
def empty_result():
    return DiffResult(
        added_rows=[], removed_rows=[], modified_rows=[],
        added_columns=[], removed_columns=[]
    )


@pytest.fixture
def full_result():
    return DiffResult(
        added_rows=[{"id": "3", "name": "Carol"}],
        removed_rows=[{"id": "2", "name": "Bob"}],
        modified_rows=[("1", {"id": "1", "name": "Alice"}, {"id": "1", "name": "Alicia"})],
        added_columns=["email"],
        removed_columns=["phone"],
    )


def test_export_json_structure(full_result):
    output = export_json(full_result)
    data = json.loads(output)
    assert "added_rows" in data
    assert "removed_rows" in data
    assert "modified_rows" in data
    assert "added_columns" in data
    assert "removed_columns" in data


def test_export_json_values(full_result):
    data = json.loads(export_json(full_result))
    assert data["added_columns"] == ["email"]
    assert data["removed_columns"] == ["phone"]
    assert len(data["modified_rows"]) == 1
    assert data["modified_rows"][0]["key"] == "1"


def test_export_csv_headers(full_result):
    output = export_csv(full_result)
    first_line = output.splitlines()[0]
    assert "change_type" in first_line
    assert "key" in first_line
    assert "field" in first_line


def test_export_csv_contains_changes(full_result):
    output = export_csv(full_result)
    assert "added" in output
    assert "removed" in output
    assert "modified" in output


def test_export_markdown_headings(full_result):
    output = export_markdown(full_result)
    assert "# CSV Diff Report" in output
    assert "## Added Columns" in output
    assert "## Removed Columns" in output
    assert "## Modified Rows" in output


def test_export_markdown_empty(empty_result):
    output = export_markdown(empty_result)
    assert "# CSV Diff Report" in output
    assert "Added Rows" not in output


def test_export_diff_dispatch_json(full_result):
    opts = ExportOptions(format="json")
    out = export_diff(full_result, opts)
    json.loads(out)  # should not raise


def test_export_diff_dispatch_csv(full_result):
    opts = ExportOptions(format="csv")
    out = export_diff(full_result, opts)
    assert "change_type" in out


def test_export_diff_dispatch_markdown(full_result):
    opts = ExportOptions(format="markdown")
    out = export_diff(full_result, opts)
    assert "#" in out


def test_export_diff_invalid_format(full_result):
    opts = ExportOptions(format="xml")  # type: ignore
    with pytest.raises(ValueError, match="Unsupported format"):
        export_diff(full_result, opts)
