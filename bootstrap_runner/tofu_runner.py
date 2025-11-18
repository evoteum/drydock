from argparse import ArgumentParser
from pathlib import Path

import subprocess
from typing import Optional, Any


class TofuInitError(Exception):
    """Raised when tofu init fails."""


class TofuApplyError(Exception):
    """Raised when tofu apply fails."""


def build_option_args(option: str, **cfg) -> list[str]:
    return [f"{option}={key}={value}" for key, value in cfg.items()]


def real_tofu_init(
    backend_bucket: str,
    backend_region: str,
    backend_key: str,
    config_path: str = None,
) -> None:
    """
    Initialise an OpenTofu configuration using a remote backend.

    Parameters:
        backend_bucket (str): Storage bucket for the backend.
        backend_region (str): Region for the backend.
        backend_key (str): Object key in the backend bucket.
        config_path (str): Path to the tofu configuration.

    Raises:
        TofuInitError: When tofu init returns a non-zero status.
    """
    required_fields = {
        "backend_bucket": backend_bucket,
        "backend_region": backend_region,
        "backend_key": backend_key,
        "config_path": config_path,
    }

    for name, value in required_fields.items():
        if not value:
            raise TofuInitError(f"{name} is required")

    if not Path(config_path).exists():
        raise TofuInitError(f"Config path does not exist: {config_path}")

    main_tofu = Path(f"{config_path}/main.tofu")
    if not main_tofu.is_file():
        raise TofuInitError(f"OpenTofu main.tofu not found in: {config_path}")

    backend_args = build_option_args(
        option="-backend-config",
        bucket=backend_bucket,
        region=backend_region,
        key=backend_key,
    )

    command = [
        "tofu",
        "init",
        f"-chdir={config_path}",
        "-input=false",
        "-no-color",
    ] + backend_args

    try:
        result = subprocess.run(command, check=False, text=True, capture_output=True)
    except FileNotFoundError as exc:
        raise TofuInitError(
            "The 'tofu' command was not found. Please ensure OpenTofu is installed and available on PATH."
        ) from exc

    if result.returncode != 0:
        raise TofuInitError(
            f"OpenTofu initialisation failed.\nSTDERR:\n{result.stderr}"
        )


def real_tofu_apply(config_path: str = None, **tf_vars: Any) -> None:
    """
    Apply an OpenTofu configuration with optional variable overrides.

    Parameters:
        **tf_vars: Arbitrary key=value pairs translated to -var flags.
        config_path (str): Path to the tofu configuration.


    Raises:
        TofuApplyError: When tofu apply returns a non-zero exit status.
    """
    if not config_path:
        raise TofuApplyError("config_path is required for real_tofu_apply.")
    if not Path(config_path).exists():
        raise TofuApplyError(f"Config path does not exist: {config_path}")
    main_tofu = Path(f"{config_path}/main.tofu")
    if not main_tofu.is_file():
        raise TofuInitError(f"OpenTofu main.tofu not found in: {config_path}")

    var_flags = build_option_args(option="-var", **tf_vars)

    command = [
        "tofu",
        "apply",
        f"-chdir={config_path}",
        "-no-color",
        "-auto-approve",
    ] + var_flags

    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise TofuApplyError(
            "The 'tofu' executable was not found. Ensure OpenTofu is installed and available on PATH."
        ) from exc

    if result.returncode != 0:
        raise TofuApplyError(f"OpenTofu apply failed.\nSTDERR:\n{result.stderr}")
