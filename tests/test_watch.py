"""Tests for csvdiff.watch module."""

import os
import pytest
from unittest.mock import patch, MagicMock
from csvdiff.watch import WatchOptions, WatchError, watch_files, _mtime


def test_mtime_returns_float(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("a,b\n1,2")
    result = _mtime(str(f))
    assert isinstance(result, float)


def test_mtime_raises_on_missing():
    with pytest.raises(WatchError, match="Cannot stat"):
        _mtime("/nonexistent/file.csv")


def test_watch_raises_on_empty_paths():
    with pytest.raises(WatchError, match="No paths"):
        watch_files([], callback=lambda c: None, options=WatchOptions(max_iterations=1))


def test_watch_no_change_no_callback(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("a,b\n1,2")
    called = []

    watch_files(
        [str(f)],
        callback=lambda c: called.append(c),
        options=WatchOptions(interval=0, max_iterations=2),
    )

    assert called == []


def test_watch_detects_change(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("a,b\n1,2")
    called = []
    iterations = [0]

    def fake_sleep(_):
        if iterations[0] == 0:
            f.write_text("a,b\n3,4")
            # bump mtime explicitly
            current = os.path.getmtime(str(f))
            os.utime(str(f), (current + 10, current + 10))
        iterations[0] += 1

    with patch("csvdiff.watch.time.sleep", side_effect=fake_sleep):
        watch_files(
            [str(f)],
            callback=lambda c: called.append(c),
            options=WatchOptions(interval=0, max_iterations=2),
        )

    assert len(called) == 1
    assert str(f) in called[0]


def test_watch_options_defaults():
    opts = WatchOptions()
    assert opts.interval == 1.0
    assert opts.max_iterations is None
