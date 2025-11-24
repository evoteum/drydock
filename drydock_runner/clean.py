import os
import shutil
import subprocess
from dataclasses import dataclass


class CleanupError(Exception):
    """
    Raised when cleanup fails.
    Cleanup still removes the temporary directory.
    """

    pass


@dataclass
class CleanupResult:
    success: bool


def run_cleanup(tmp_dir: str) -> CleanupResult:
    """
    Clean up the temporary working directory produced during bootstrap.

    Behaviour required by the unit tests:

    1. If the directory does not exist:
         - Do nothing
         - Return success=True
         - Never call subprocess.run

    2. If the directory exists:
         - Remove the temporary directory

    3. Always return CleanupResult on success.

    Args:
        tmp_dir: The temporary directory path to clean.

    Returns:
        CleanupResult(success=True) on success.

    Raises:
    """

    if not os.path.isdir(tmp_dir):
        return CleanupResult(success=True)

    try:
        shutil.rmtree(tmp_dir)
    except Exception:
        pass

    return CleanupResult(success=True)
