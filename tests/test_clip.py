"""Tests for csvdiff.clip and csvdiff.cli_clip."""

from __future__ import annotations

import argparse
import sys
from unittest.mock import MagicMock, patch

import pytest

from csvdiff.clip import (
    ClipError,
    ClipOptions,
    _get_copy_command,
    copy_to_clipboard,
    maybe_copy_to_clipboard,
)
from csvdiff.cli_clip import (
    clip_options_from_args,
    handle_clip,
    register_clip_args,
)


# ---------------------------------------------------------------------------
# _get_copy_command
# ---------------------------------------------------------------------------

def test_get_copy_command_macos():
    with patch.object(sys, "platform", "darwin"):
        assert _get_copy_command() == ["pbcopy"]


def test_get_copy_command_linux():
    with patch.object(sys, "platform", "linux"):
        assert _get_copy_command() == ["xclip", "-selection", "clipboard"]


def test_get_copy_command_windows():
    with patch.object(sys, "platform", "win32"):
        assert _get_copy_command() == ["clip"]


def test_get_copy_command_unknown_raises():
    with patch.object(sys, "platform", "freebsd14"):
        with pytest.raises(ClipError, match="Unsupported platform"):
            _get_copy_command()


# ---------------------------------------------------------------------------
# copy_to_clipboard
# ---------------------------------------------------------------------------

def test_copy_to_clipboard_empty_raises():
    with pytest.raises(ClipError, match="empty"):
        copy_to_clipboard("")


def test_copy_to_clipboard_calls_subprocess():
    mock_result = MagicMock(returncode=0)
    with patch("csvdiff.clip.subprocess.run", return_value=mock_result) as mock_run:
        with patch.object(sys, "platform", "darwin"):
            copy_to_clipboard("hello")
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == ["pbcopy"]
    assert kwargs["input"] == b"hello"


def test_copy_to_clipboard_nonzero_exit_raises():
    mock_result = MagicMock(returncode=1, stderr=b"oops")
    with patch("csvdiff.clip.subprocess.run", return_value=mock_result):
        with patch.object(sys, "platform", "darwin"):
            with pytest.raises(ClipError, match="failed"):
                copy_to_clipboard("data")


def test_copy_to_clipboard_missing_command_raises():
    with patch("csvdiff.clip.subprocess.run", side_effect=FileNotFoundError("pbcopy")):
        with patch.object(sys, "platform", "darwin"):
            with pytest.raises(ClipError, match="not found"):
                copy_to_clipboard("data")


# ---------------------------------------------------------------------------
# maybe_copy_to_clipboard
# ---------------------------------------------------------------------------

def test_maybe_copy_none_opts_returns_false():
    assert maybe_copy_to_clipboard("text", None) is False


def test_maybe_copy_disabled_returns_false():
    opts = ClipOptions(enabled=False)
    assert maybe_copy_to_clipboard("text", opts) is False


def test_maybe_copy_enabled_calls_copy():
    opts = ClipOptions(enabled=True)
    with patch("csvdiff.clip.copy_to_clipboard") as mock_copy:
        result = maybe_copy_to_clipboard("hello", opts)
    mock_copy.assert_called_once_with("hello")
    assert result is True


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_clip_args(p)
    return p


def test_register_clip_args_copy_default_false(parser):
    args = parser.parse_args([])
    assert args.copy is False


def test_register_clip_args_copy_flag(parser):
    args = parser.parse_args(["--copy"])
    assert args.copy is True


def test_register_clip_args_format_default(parser):
    args = parser.parse_args([])
    assert args.copy_format == "text"


def test_clip_options_from_args_none_when_not_set(parser):
    args = parser.parse_args([])
    assert clip_options_from_args(args) is None


def test_clip_options_from_args_returns_options(parser):
    args = parser.parse_args(["--copy", "--copy-format", "csv"])
    opts = clip_options_from_args(args)
    assert opts is not None
    assert opts.enabled is True
    assert opts.format == "csv"


def test_handle_clip_prints_confirmation(parser, capsys):
    args = parser.parse_args(["--copy"])
    with patch("csvdiff.cli_clip.maybe_copy_to_clipboard", return_value=True):
        handle_clip("output text", args)
    captured = capsys.readouterr()
    assert "copied to clipboard" in captured.out


def test_handle_clip_prints_error_on_failure(parser, capsys):
    args = parser.parse_args(["--copy"])
    with patch("csvdiff.cli_clip.maybe_copy_to_clipboard", side_effect=ClipError("boom")):
        handle_clip("output text", args)
    captured = capsys.readouterr()
    assert "Clipboard error" in captured.out
