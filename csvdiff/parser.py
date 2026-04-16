"""CSV parsing utilities for csvdiff."""

import csv
from pathlib import Path
from typing import List, Dict, Tuple


class CSVParseError(Exception):
    """Raised when a CSV file cannot be parsed."""
    pass


def load_csv(filepath: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Load a CSV file and return (headers, rows).

    Args:
        filepath: Path to the CSV file.

    Returns:
        A tuple of (headers, rows) where rows is a list of dicts.

    Raises:
        CSVParseError: If the file cannot be read or parsed.
    """
    path = Path(filepath)

    if not path.exists():
        raise CSVParseError(f"File not found: {filepath}")

    if not path.is_file():
        raise CSVParseError(f"Not a file: {filepath}")

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise CSVParseError(f"Empty or invalid CSV file: {filepath}")

            headers = list(reader.fieldnames)
            rows = [dict(row) for row in reader]

        return headers, rows

    except (OSError, csv.Error) as exc:
        raise CSVParseError(f"Failed to parse {filepath}: {exc}") from exc


def detect_delimiter(filepath: str) -> str:
    """Attempt to auto-detect the delimiter of a CSV file."""
    path = Path(filepath)
    try:
        with open(path, newline="", encoding="utf-8") as f:
            sample = f.read(4096)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except (OSError, csv.Error):
        return ","
