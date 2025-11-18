import os
import pytest

from bootstrap_runner.environment import (
    validate_environment,
    validate_ip_address,
    EnvironmentValidationError,
    InvalidIPAddressError,
)


def clear_env():
    """Utility helper to clear required configuration variables."""
    for var in ["TF_BACKEND_BUCKET", "TF_BACKEND_KEY", "TF_BACKEND_REGION"]:
        if var in os.environ:
            del os.environ[var]


def set_valid_env():
    """Utility helper to populate valid environment variables."""
    os.environ["TF_BACKEND_BUCKET"] = "example-bucket"
    os.environ["TF_BACKEND_KEY"] = "some/key"
    os.environ["TF_BACKEND_REGION"] = "eu-west-2"


# ---------------------------------------------------------------------------
# Environment validation tests
# ---------------------------------------------------------------------------


def test_validate_environment_succeeds_with_all_variables_present():
    """Environment validation should return True when all variables exist."""
    clear_env()
    set_valid_env()

    result = validate_environment()
    assert result is True


def test_validate_environment_fails_when_variables_missing():
    """
    If one or more mandatory variables are missing, validation should fail
    with a clear, domain-specific exception rather than an exciting stack trace.
    """
    clear_env()  # simulate zero configuration

    with pytest.raises(EnvironmentValidationError):
        validate_environment()


def test_validate_environment_fails_if_only_some_variables_present():
    """Partial configuration should still raise an error."""
    clear_env()
    os.environ["TF_BACKEND_BUCKET"] = "bucket-only"

    with pytest.raises(EnvironmentValidationError):
        validate_environment()


# ---------------------------------------------------------------------------
# IP address validation tests
# ---------------------------------------------------------------------------


def test_validate_ip_address_accepts_valid_ipv4():
    """A correct IPv4 address should pass and return a normalised string."""
    ip = "192.168.8.50"
    result = validate_ip_address(ip)
    assert result == "192.168.8.50"


def test_validate_ip_address_normalises_weird_but_valid_input():
    """
    The ipaddress library normalises IPv4 strings.
    This ensures our validation behaves predictably.
    """
    ip = "192.168.008.050"  # unusual but technically valid
    result = validate_ip_address(ip)
    assert (
        result == "192.168.8.50"
    ), "IP should be normalised to a standard dotted-decimal format."


def test_validate_ip_address_rejects_gibberish():
    """Invalid IPv4 values should raise InvalidIPAddressError."""
    with pytest.raises(InvalidIPAddressError):
        validate_ip_address("this-is-not-an-ip")


def test_validate_ip_address_rejects_out_of_range_values():
    """Numerically invalid octets should also raise our domain error."""
    with pytest.raises(InvalidIPAddressError):
        validate_ip_address("999.999.999.999")


def test_validate_ip_address_rejects_partial_addresses():
    """Anything non-IPv4 should raise an error."""
    with pytest.raises(InvalidIPAddressError):
        validate_ip_address("192.168.1")


def test_validate_ip_address_rejects_empty_string():
    """Empty or whitespace-only input should be invalid."""
    with pytest.raises(InvalidIPAddressError):
        validate_ip_address("   ")
