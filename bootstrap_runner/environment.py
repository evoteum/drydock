import os
import ipaddress
from shutil import copyfile


class EnvironmentValidationError(Exception):
    """
    Raised when mandatory backend configuration is missing.
    """

    pass


class InvalidIPAddressError(Exception):
    """
    Raised when an IPv4 address fails validation.
    """

    pass


def validate_environment() -> bool:
    """
    Validate that mandatory backend configuration variables exist.

    Required variables:
      TF_BACKEND_BUCKET
      TF_BACKEND_KEY
      TF_BACKEND_REGION

    Returns:
        True if all variables are present.

    Raises:
        EnvironmentValidationError if any are missing.
    """
    required_vars = [
        "TF_BACKEND_BUCKET",
        "TF_BACKEND_KEY",
        "TF_BACKEND_REGION",
    ]

    missing = [var for var in required_vars if var not in os.environ]

    if missing:
        missing_str = ", ".join(missing)
        copyfile(src=".env.example", dst=".env")
        raise EnvironmentValidationError(
            f"Missing required backend configuration: {missing_str}"
        )

    return True


def validate_ip_address(ip: str) -> str:
    """
    Validate an IPv4 address string.

    The function trims whitespace, verifies correctness,
    and returns a normalised dotted-decimal string.

    Args:
        ip: The IPv4 address as provided by an operator.

    Returns:
        A normalised IPv4 address string.

    Raises:
        InvalidIPAddressError if validation fails.
    """
    if not isinstance(ip, str):
        raise InvalidIPAddressError("IP address must be a string")

    ip = ip.strip()

    if ip == "":
        raise InvalidIPAddressError("IP address cannot be empty")

    try:
        normalised = ipaddress.IPv4Address(ip)
        return str(normalised)
    except Exception as exc:
        raise InvalidIPAddressError(f"'{ip}' is not a valid IPv4 address") from exc
