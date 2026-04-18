"""CLI integration for --watch mode in csvdiff."""

from typing import Optional
from csvdiff.watch import WatchOptions, WatchError, watch_files
from csvdiff.pipeline import run_pipeline, PipelineResult
from csvdiff.reporter import build_report, render_report, report_exit_code
from csvdiff.config import CsvDiffConfig


def _run_and_print(file_a: str, file_b: str, config: CsvDiffConfig) -> None:
    """Execute the diff pipeline and print the report."""
    try:
        result: PipelineResult = run_pipeline(file_a, file_b, config)
        report = build_report(result)
        print(render_report(report, config))
    except Exception as e:  # noqa: BLE001
        print(f"[csvdiff] Error during diff: {e}")


def start_watch(
    file_a: str,
    file_b: str,
    config: CsvDiffConfig,
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Watch file_a and file_b and re-run diff on any change.

    Prints an initial diff immediately, then re-runs whenever either
    file is modified.
    """
    print(f"[csvdiff] Watching {file_a!r} and {file_b!r} (interval={interval}s) ...")
    _run_and_print(file_a, file_b, config)

    def on_change(changed: list[str]) -> None:
        print(f"[csvdiff] Change detected in: {', '.join(changed)}")
        _run_and_print(file_a, file_b, config)

    options = WatchOptions(interval=interval, max_iterations=max_iterations)
    try:
        watch_files([file_a, file_b], callback=on_change, options=options)
    except WatchError as e:
        raise SystemExit(f"[csvdiff] Watch error: {e}") from e
    except KeyboardInterrupt:
        print("\n[csvdiff] Watch stopped.")
