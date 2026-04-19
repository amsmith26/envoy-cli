"""Tests for envoy_cli.watch"""

import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from envoy_cli.watch import get_mtime, watch_env_file, make_push_handler


def test_get_mtime_existing_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=val")
    mtime = get_mtime(str(f))
    assert isinstance(mtime, float)
    assert mtime > 0


def test_get_mtime_missing_file(tmp_path):
    assert get_mtime(str(tmp_path / "nonexistent.env")) is None


def test_watch_detects_change(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=original")

    calls = []

    def on_change(path):
        calls.append(path)

    # We'll patch time.sleep and manually bump mtime between iterations
    original_sleep = time.sleep
    iteration = [0]

    def fake_sleep(interval):
        iteration[0] += 1
        if iteration[0] == 1:
            # Modify the file to trigger change detection
            env_file.write_text("KEY=updated")
            # Force mtime difference
            new_mtime = env_file.stat().st_mtime + 1
            import os
            os.utime(str(env_file), (new_mtime, new_mtime))

    with patch("time.sleep", side_effect=fake_sleep):
        watch_env_file(str(env_file), on_change, interval=0.01, max_iterations=2)

    assert len(calls) == 1
    assert calls[0] == str(env_file)


def test_watch_no_change(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=stable")

    calls = []

    with patch("time.sleep"):
        watch_env_file(str(env_file), lambda p: calls.append(p), interval=0.01, max_iterations=3)

    assert calls == []


def test_make_push_handler(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar")
    vault_file = str(tmp_path / "vault.env.vault")

    with patch("envoy_cli.watch.push_env") as mock_push, \
         patch("envoy_cli.watch.record_event") as mock_record:
        handler = make_push_handler(vault_file, "production", "secret")
        handler(str(env_file))

        mock_push.assert_called_once_with(str(env_file), vault_file, "production", "secret")
        mock_record.assert_called_once()
        args = mock_record.call_args[0]
        assert args[1] == "watch-push"
        assert args[2] == "production"
