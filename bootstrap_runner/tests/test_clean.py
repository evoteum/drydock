import os
import tempfile
from unittest.mock import patch

import pytest

from bootstrap_runner.clean import run_cleanup, CleanupError


def create_fake_infra(tmp_dir: str):
    """
    Create a minimal directory structure that simulates what the cleanup
    code expects. This avoids inventing domain detail and only builds
    what the cleanup logic actually interacts with.
    """
    tofu_dir = os.path.join(tmp_dir, "tofu", "development")
    os.makedirs(tofu_dir, exist_ok=True)

    # Create a dummy file to ensure the directory is not empty.
    dummy_state = os.path.join(tofu_dir, "state.tf")
    with open(dummy_state, "w", encoding="utf8") as fh:
        fh.write("placeholder")

    return tofu_dir, dummy_state


@patch("python.clean.subprocess.run")
def test_cleanup_runs_tofu_and_removes_directory(mock_run):
    """
    A successful cleanup should:
    1. Run the tofu apply command.
    2. Remove the temporary directory afterwards.
    """
    tmp_dir = tempfile.mkdtemp(prefix="cleanup-test-")
    tofu_dir, dummy_file = create_fake_infra(tmp_dir)

    # Run cleanup
    result = run_cleanup(tmp_dir)

    # Expectations about subprocess calls
    # Ensure tofu was called with the expected arguments.
    mock_run.assert_called_once()
    assert (
        "tofu" in mock_run.call_args[0][0]
    ), "Expected cleanup to run a tofu command, but it did not."

    # The directory should be gone
    assert not os.path.exists(
        tmp_dir
    ), "Cleanup did not remove the temporary directory."

    # The function should return a success indicator
    assert result.success is True, "Cleanup did not return a success result."


@patch("python.clean.subprocess.run")
def test_cleanup_handles_missing_directory(mock_run):
    """
    If the directory does not exist, cleanup should treat this as a
    no-op and not crash.
    """
    missing_dir = "/tmp/this/does/not/exist"

    result = run_cleanup(missing_dir)

    # Subprocess should not be called, because nothing exists to apply cleanup to.
    mock_run.assert_not_called()

    assert result.success is True, "Cleanup should succeed when directory is missing."


@patch("python.clean.subprocess.run", side_effect=Exception("tofu error"))
def test_cleanup_handles_tofu_failure(mock_run):
    """
    If tofu apply fails, cleanup should surface a readable CleanupError
    but still attempt to remove the directory safely.
    """
    tmp_dir = tempfile.mkdtemp(prefix="cleanup-test-fail-")
    tofu_dir, dummy_file = create_fake_infra(tmp_dir)

    with pytest.raises(CleanupError):
        run_cleanup(tmp_dir)

    # Directory should still be removed even on failure.
    assert not os.path.exists(
        tmp_dir
    ), "Cleanup should remove the temp directory even on tofu failure."
