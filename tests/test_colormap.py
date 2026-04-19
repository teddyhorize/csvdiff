import pytest
from csvdiff.colormap import (
    Colormap,
    ColormapError,
    DEFAULT_COLORS,
    ANSI_RESET,
    default_colormap,
    build_colormap,
    format_colormap_legend,
)


def test_default_colormap_has_all_labels():
    cm = default_colormap()
    for label in ("added", "removed", "modified", "unchanged", "header"):
        assert label in cm.colors


def test_default_colormap_values_match():
    cm = default_colormap()
    assert cm.colors == DEFAULT_COLORS


def test_get_known_label():
    cm = default_colormap()
    assert cm.get("added") == DEFAULT_COLORS["added"]


def test_get_unknown_label_returns_reset():
    cm = default_colormap()
    assert cm.get("nonexistent") == ANSI_RESET


def test_apply_wraps_text():
    cm = default_colormap()
    result = cm.apply("added", "hello")
    assert "hello" in result
    assert result.endswith(ANSI_RESET)
    assert result.startswith(DEFAULT_COLORS["added"])


def test_build_colormap_override():
    cm = build_colormap({"added": "\033[34m"})
    assert cm.get("added") == "\033[34m"
    assert cm.get("removed") == DEFAULT_COLORS["removed"]


def test_build_colormap_invalid_label_raises():
    with pytest.raises(ColormapError, match="Unknown color labels"):
        build_colormap({"bogus": "\033[0m"})


def test_build_colormap_multiple_invalids():
    with pytest.raises(ColormapError):
        build_colormap({"x": "", "y": ""})


def test_format_colormap_legend_length():
    cm = default_colormap()
    lines = format_colormap_legend(cm)
    assert len(lines) == 5


def test_format_colormap_legend_contains_labels():
    cm = default_colormap()
    legend = "\n".join(format_colormap_legend(cm))
    for label in ("added", "removed", "modified"):
        assert label in legend
