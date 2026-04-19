import argparse
import pytest
from csvdiff.cli_colormap import (
    register_colormap_args,
    colormap_from_args,
    maybe_print_legend,
    _parse_override,
)
from csvdiff.colormap import ColormapError, DEFAULT_COLORS


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    register_colormap_args(p)
    return p


def test_register_colormap_args(parser):
    args = parser.parse_args([])
    assert hasattr(args, "color_overrides")
    assert hasattr(args, "no_color")
    assert hasattr(args, "show_color_legend")


def test_no_color_flag(parser):
    args = parser.parse_args(["--no-color"])
    assert args.no_color is True


def test_colormap_from_args_default(parser):
    args = parser.parse_args([])
    cm = colormap_from_args(args)
    assert cm is not None
    assert cm.colors == DEFAULT_COLORS


def test_colormap_from_args_no_color_returns_none(parser):
    args = parser.parse_args(["--no-color"])
    assert colormap_from_args(args) is None


def test_colormap_from_args_with_override(parser):
    args = parser.parse_args(["--color", "added=\033[34m"])
    cm = colormap_from_args(args)
    assert cm is not None
    assert cm.get("added") == "\033[34m"


def test_colormap_from_args_invalid_override(parser):
    args = parser.parse_args(["--color", "badlabel=\033[0m"])
    with pytest.raises(ColormapError):
        colormap_from_args(args)


def test_parse_override_valid():
    label, code = _parse_override("added=\033[34m")
    assert label == "added"
    assert code == "\033[34m"


def test_parse_override_no_equals_raises():
    with pytest.raises(ColormapError):
        _parse_override("addedonly")


def test_maybe_print_legend_false_when_not_set(parser, capsys):
    args = parser.parse_args([])
    from csvdiff.colormap import default_colormap
    result = maybe_print_legend(args, default_colormap())
    assert result is False
    assert capsys.readouterr().out == ""


def test_maybe_print_legend_prints_when_flag(parser, capsys):
    args = parser.parse_args(["--show-color-legend"])
    from csvdiff.colormap import default_colormap
    result = maybe_print_legend(args, default_colormap())
    assert result is True
    out = capsys.readouterr().out
    assert len(out) > 0
