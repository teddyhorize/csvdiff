"""High-level pipeline: load, filter, schema-check, diff two CSV files."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from csvdiff.parser import load_csv
from csvdiff.filter import FilterOptions, apply_filters
from csvdiff.schema import SchemaDiff, compare_schemas
from csvdiff.differ import DiffResult, diff_csv


@dataclass
class PipelineResult:
    schema_diff: SchemaDiff
    diff: DiffResult
    left_row_count: int
    right_row_count: int


def run_pipeline(
    left_path: str,
    right_path: str,
    key_column: str,
    filter_options: Optional[FilterOptions] = None,
) -> PipelineResult:
    """Load two CSV files, apply filters, compare schemas, and diff rows."""
    if filter_options is None:
        filter_options = FilterOptions()

    left_rows = load_csv(left_path)
    right_rows = load_csv(right_path)

    left_headers = list(left_rows[0].keys()) if left_rows else []
    right_headers = list(right_rows[0].keys()) if right_rows else []
    schema_diff = compare_schemas(left_headers, right_headers)

    left_filtered = apply_filters(left_rows, filter_options)
    right_filtered = apply_filters(right_rows, filter_options)

    diff = diff_csv(left_filtered, right_filtered, key_column=key_column)

    return PipelineResult(
        schema_diff=schema_diff,
        diff=diff,
        left_row_count=len(left_rows),
        right_row_count=len(right_rows),
    )
