"""Tests for the reporter module."""
import pytest
from unittest.mock import MagicMock
from csvdiff.differ import DiffResult
from csvdiff.pipeline import PipelineResult
from csvdiff.reporter import Report, build_report, render_report
from csvdiff.formatter import FormatOptions


@pytest.fixture
def clean_pipeline_result():
    diff = DiffResult(added=[], removed=[], modified=[], added_columns=[], removed_columns=[])
    return PipelineResult(
        diff_result=diff,
        headers_a=["id", "name"],
        headers_b=["id", "name"],
        row_count_a=3,
        row_count_b=3,
    )


@pytest.fixture
def dirty_pipeline_result():
    diff = DiffResult(
        added=[{"id": "4", "name": "Dave"}],
        removed=[{"id": "1", "name": "Alice"}],
        modified=[],
        added_columns=[],
        removed_columns=[],
    )
    return PipelineResult(
        diff_result=diff,
        headers_a=["id", "name"],
        headers_b=["id", "name", "email"],
        row_count_a=3,
        row_count_b=3,
    )


def test_build_report_clean(clean_pipeline_result):
    report = build_report(clean_pipeline_result)
    assert isinstance(report, Report)
    assert report.is_clean


def test_build_report_dirty(dirty_pipeline_result):
    report = build_report(dirty_pipeline_result)
    assert not report.is_clean


def test_build_report_has_summary(dirty_pipeline_result):
    report = build_report(dirty_pipeline_result)
    assert report.summary is not None
    assert report.summary_text


def test_build_report_schema_diff(dirty_pipeline_result):
    report = build_report(dirty_pipeline_result)
    assert report.schema_diff.has_changes
    assert "email" in report.schema_text


def test_render_report_no_verbose(dirty_pipeline_result):
    report = build_report(dirty_pipeline_result)
    text = render_report(report, verbose=False)
    assert isinstance(text, str)
    assert report.summary_text not in text


def test_render_report_verbose(dirty_pipeline_result):
    report = build_report(dirty_pipeline_result)
    text = render_report(report, verbose=True)
    assert report.summary_text in text


def test_render_report_includes_schema(dirty_pipeline_result):
    report = build_report(dirty_pipeline_result)
    text = render_report(report)
    assert report.schema_text in text


def test_render_report_clean_no_schema(clean_pipeline_result):
    report = build_report(clean_pipeline_result)
    text = render_report(report)
    assert report.schema_text not in text
