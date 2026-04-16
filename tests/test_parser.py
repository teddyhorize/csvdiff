"""Tests for csvdiff.parser module."""

import csv
import pytest
from pathlib import Path

from csvdiff.parser import load_csv, detect_delimiter, CSVParseError


@pytest.fixture
def simple_csv(tmp_path: Path) -> Path:
    f = tmp_path / "simple.csv"
    f.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n", encoding="utf-8")
    return f


@pytest.fixture
def semicolon_csv(tmp_path: Path) -> Path:
    f = tmp_path / "semi.csv"
    f.write_text("name;age;city\nAlice;30;NYC\n", encoding="utf-8")
    return f


def test_load_csv_headers(simple_csv):
    headers, _ = load_csv(str(simple_csv))
    assert headers == ["name", "age", "city"]


def test_load_csv_row_count(simple_csv):
    _, rows = load_csv(str(simple_csv))
    assert len(rows) == 2


def test_load_csv_row_values(simple_csv):
    _, rows = load_csv(str(simple_csv))
    assert rows[0] == {"name": "Alice", "age": "30", "city": "NYC"}
    assert rows[1] == {"name": "Bob", "age": "25", "city": "LA"}


def test_load_csv_file_not_found():
    with pytest.raises(CSVParseError, match="File not found"):
        load_csv("/nonexistent/path/file.csv")


def test_load_csv_empty_file(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(CSVParseError):
        load_csv(str(empty))


def test_detect_delimiter_comma(simple_csv):
    assert detect_delimiter(str(simple_csv)) == ","


def test_detect_delimiter_semicolon(semicolon_csv):
    assert detect_delimiter(str(semicolon_csv)) == ";"


def test_detect_delimiter_fallback_on_missing():
    result = detect_delimiter("/nonexistent/file.csv")
    assert result == ","
