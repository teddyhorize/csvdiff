"""CLI integration for template-based output."""
from __future__ import annotations
import argparse
from typing import Optional

from csvdiff.template import TemplateOptions, TemplateError, render_template
from csvdiff.differ import DiffResult


def register_template_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--template",
        metavar="TMPL",
        help="Output template string using {label} and column name placeholders",
    )
    parser.add_argument(
        "--template-sep",
        default="\n",
        metavar="SEP",
        help="Separator between rendered rows (default: newline)",
    )


def template_options_from_args(args: argparse.Namespace) -> Optional[TemplateOptions]:
    tmpl = getattr(args, "template", None)
    if not tmpl:
        return None
    sep = getattr(args, "template_sep", "\n")
    return TemplateOptions(template=tmpl, separator=sep)


def maybe_render_template(result: DiffResult, args: argparse.Namespace) -> bool:
    opts = template_options_from_args(args)
    if opts is None:
        return False
    try:
        output = render_template(result, opts)
        if output:
            print(output)
    except TemplateError as e:
        print(f"Template error: {e}")
    return True
