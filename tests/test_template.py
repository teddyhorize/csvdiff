"""Tests for csvdiff/template.py"""
import pytest
from csvdiff.differ import DiffResult
from csvdiff.template import (
    TemplateOptions,
    TemplateError,
    render_row,
    render_template,
    default_template_options,
)


@pytest.fixture
def result():
    return DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[({"id": "3", "name": "Carol"}, {"id": "3", "name": "Caroline"})],
        added_columns=[],
        removed_columns=[],
    )


def test_render_row_basic():
    opts = TemplateOptions(template="{label}: {id}")
    out = render_row({"id": "42"}, "ADDED", opts)
    assert out == "ADDED: 42"


def test_render_row_unknown_key_raises():
    opts = TemplateOptions(template="{label}: {missing_col}")
    with pytest.raises(TemplateError):
        render_row({"id": "1"}, "ADDED", opts)


def test_render_template_added(result):
    opts = TemplateOptions(template="{label}|{id}|{name}")
    out = render_template(result, opts)
    assert "ADDED|1|Alice" in out


def test_render_template_removed(result):
    opts = TemplateOptions(template="{label}|{id}")
    out = render_template(result, opts)
    assert "REMOVED|2" in out


def test_render_template_modified_uses_new_value(result):
    opts = TemplateOptions(template="{label}|{id}|{name}")
    out = render_template(result, opts)
    assert "MODIFIED|3|Caroline" in out


def test_render_template_separator(result):
    opts = TemplateOptions(template="{label}", separator="---")
    out = render_template(result, opts)
    assert "---" in out


def test_render_template_empty_result():
    empty = DiffResult(added=[], removed=[], modified=[], added_columns=[], removed_columns=[])
    opts = TemplateOptions(template="{label}")
    assert render_template(empty, opts) == ""


def test_default_template_options_default():
    opts = default_template_options()
    assert "{label}" in opts.template


def test_default_template_options_custom():
    opts = default_template_options("{label} -> {id}")
    assert opts.template == "{label} -> {id}"
