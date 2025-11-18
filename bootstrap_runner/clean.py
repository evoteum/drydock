import os
import shutil
import subprocess
from dataclasses import dataclass


class CleanupError(Exception):
    """
    Raised when cleanup fails due to tofu apply errors.
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
         - Attempt to run tofu apply to disable DHCP or undo provisioning
         - Remove the temporary directory afterwards
         - If tofu fails, raise CleanupError but still remove the directory

    3. Always return CleanupResult on success.

    Args:
        tmp_dir: The temporary directory path to clean.

    Returns:
        CleanupResult(success=True) on success.

    Raises:
        CleanupError if tofu apply fails.
    """

    if not os.path.isdir(tmp_dir):
        return CleanupResult(success=True)

    tofu_args = [
        "tofu",
        "apply",
        f"-chdir={tmp_dir}/tofu/development",
        "-auto-approve",
        "-no-color",
        "-var=dhcp_enabled=false",
    ]
    tofu_error = None

    try:
        subprocess.run(tofu_args, check=True)
    except Exception as exc:
        tofu_error = exc

    try:
        shutil.rmtree(tmp_dir)
    except Exception:
        pass

    if tofu_error:
        raise CleanupError(str(tofu_error))

    return CleanupResult(success=True)
