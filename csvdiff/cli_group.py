"""CLI helpers for the --group-by feature."""
import argparse
from csvdiff.differ import DiffResult
from csvdiff.group import group_diff, format_group_stats


def register_group_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--group-by",
        metavar="COLUMN",
        default=None,
        help="Group diff statistics by the values in COLUMN.",
    )


def maybe_print_group_stats(
    result: DiffResult,
    column: str | None,
    use_color: bool = False,
) -> None:
    if not column:
        return
    stats = group_diff(result, column)
    text = format_group_stats(stats)
    if use_color:
        try:
            from csvdiff.formatter import _colorize
            lines = []
            for line in text.splitlines():
                if "+" in line:
                    lines.append(_colorize(line, "green"))
                elif "-" in line and "~" not in line:
                    lines.append(_colorize(line, "red"))
                else:
                    lines.append(line)
            print("\n".join(lines))
            return
        except Exception:
            pass
    print(text)


def group_options_from_args(args: argparse.Namespace) -> str | None:
    return getattr(args, "group_by", None)
