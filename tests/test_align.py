"""Tests for csvdiff.align module."""

import pytest
from csvdiff.align import (
    AlignError,
    AlignOptions,
    AlignedTable,
    compute_widths,
    pad_cell,
    align_table,
    render_table,
)

SAMPLE_HEADERS = ["name", "age", "city"]
SAMPLE_ROWS = [
    {"name": "Alice", "age": "30", "city": "New York"},
    {"name": "Bob", "age": "25", "city": "LA"},
]


def test_compute_widths_basic():
    widths = compute_widths(["id", "name"], [["1", "Alice"], ["2", "Bob"]])
    assert widths[0] >= 2  # "id"
    assert widths[1] >= 5  # "Alice"


def test_compute_widths_respects_min():
    opts = AlignOptions(min_width=10)
    widths = compute_widths(["x"], [["1"]], opts)
    assert widths[0] == 10


def test_compute_widths_respects_max():
    opts = AlignOptions(max_width=5)
    widths = compute_widths(["col"], [["a" * 20]], opts)
    assert widths[0] == 5


def test_pad_cell_pads_short():
    result = pad_cell("hi", 6)
    assert result == "hi    "
    assert len(result) == 6


def test_pad_cell_truncates_long():
    result = pad_cell("hello world", 7)
    assert len(result) == 7
    assert result.endswith("…")


def test_pad_cell_no_truncate():
    opts = AlignOptions(truncate_long=False)
    result = pad_cell("hello world", 5, opts)
    assert result == "hello world"


def test_align_table_returns_aligned_table():
    table = align_table(SAMPLE_HEADERS, SAMPLE_ROWS)
    assert isinstance(table, AlignedTable)
    assert len(table.headers) == 3
    assert len(table.rows) == 2


def test_align_table_row_lengths_match_headers():
    table = align_table(SAMPLE_HEADERS, SAMPLE_ROWS)
    for row in table.rows:
        assert len(row) == len(table.headers)


def test_align_table_empty_rows():
    table = align_table(SAMPLE_HEADERS, [])
    assert table.rows == []
    assert len(table.widths) == 3


def test_align_table_raises_on_empty_headers():
    with pytest.raises(AlignError):
        align_table([], SAMPLE_ROWS)


def test_align_table_missing_key_defaults_empty():
    rows = [{"name": "Alice"}]  # missing age, city
    table = align_table(SAMPLE_HEADERS, rows)
    assert len(table.rows[0]) == 3


def test_render_table_contains_headers():
    table = align_table(SAMPLE_HEADERS, SAMPLE_ROWS)
    output = render_table(table)
    assert "name" in output
    assert "age" in output


def test_render_table_has_separator_line():
    table = align_table(SAMPLE_HEADERS, SAMPLE_ROWS)
    output = render_table(table)
    lines = output.splitlines()
    assert set(lines[1]) <= {"-"}


def test_render_table_row_count():
    table = align_table(SAMPLE_HEADERS, SAMPLE_ROWS)
    output = render_table(table)
    lines = output.splitlines()
    # header + separator + 2 rows
    assert len(lines) == 4
