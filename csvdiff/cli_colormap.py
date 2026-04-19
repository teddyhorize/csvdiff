from __future__ import annotations
import argparse
from typing import Optional
from csvdiff.colormap import Colormap, ColormapError, build_colormap, default_colormap

_LABEL_CHOICES = ["added", "removed", "modified", "unchanged", "header"]


def register_colormap_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--color",
        metavar="LABEL=CODE",
        action="append",
        dest="color_overrides",
        default=[],
        help="Override ANSI color for a diff label, e.g. added=\\033[34m",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable all color output",
    )
    parser.add_argument(
        "--show-color-legend",
        action="store_true",
        default=False,
        help="Print the color legend and exit",
    )


def _parse_override(pair: str) -> tuple[str, str]:
    if "=" not in pair:
        raise ColormapError(f"Invalid color override (expected LABEL=CODE): {pair!r}")
    label, _, code = pair.partition("=")
    return label.strip(), code.strip()


def colormap_from_args(args: argparse.Namespace) -> Optional[Colormap]:
    if getattr(args, "no_color", False):
        return None
    overrides_raw = getattr(args, "color_overrides", []) or []
    if not overrides_raw:
        return default_colormap()
    overrides = dict(_parse_override(p) for p in overrides_raw)
    return build_colormap(overrides)


def maybe_print_legend(args: argparse.Namespace, colormap: Optional[Colormap]) -> bool:
    if not getattr(args, "show_color_legend", False):
        return False
    if colormap is None:
        print("Color output disabled.")
    else:
        from csvdiff.colormap import format_colormap_legend
        for line in format_colormap_legend(colormap):
            print(line)
    return True
