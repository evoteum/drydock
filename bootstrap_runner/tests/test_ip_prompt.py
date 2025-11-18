import pytest
from bootstrap_runner.ip_prompt import prompt_for_ip


def test_prompt_for_ip_accepts_valid_address():
    """
    A valid IP address should be accepted immediately and returned.
    """
    inputs = iter(["192.168.8.50"])
    outputs = []

    def fake_input():
        return next(inputs)

    def fake_output(msg):
        outputs.append(msg)

    result = prompt_for_ip(input_func=fake_input, output_func=fake_output)

    assert result == "192.168.8.50"
    assert "Please enter the IP address" in outputs[0]


def test_prompt_for_ip_rejects_invalid_address_and_retries():
    """
    An invalid IP should result in an error message and a retry prompt.
    The function should only return once a valid address is provided.
    """
    inputs = iter(["this-is-not-an-ip", "192.168.8.50"])  # invalid  # valid
    outputs = []

    def fake_input():
        return next(inputs)

    def fake_output(msg):
        outputs.append(msg)

    result = prompt_for_ip(input_func=fake_input, output_func=fake_output)

    assert result == "192.168.8.50"

    # Ensure error was reported
    error_lines = [line for line in outputs if "Invalid IP address" in line]
    assert len(error_lines) == 1, "Expected one invalid IP warning"

    # Ensure retry prompt was given
    retry_lines = [line for line in outputs if "Please try again" in line]
    assert len(retry_lines) == 1, "Expected one retry instruction"


def test_prompt_for_ip_handles_multiple_failures_before_success():
    """
    Even if the operator enters several invalid addresses,
    the function should continue politely prompting until success.
    """
    inputs = iter(
        [
            "",  # empty
            "999.999.999.999",  # nonsense
            "hello computer",  # still not an IP
            "10.0.0.10",  # valid at last
        ]
    )
    outputs = []

    def fake_input():
        return next(inputs)

    def fake_output(msg):
        outputs.append(msg)

    result = prompt_for_ip(input_func=fake_input, output_func=fake_output)

    assert result == "10.0.0.10"

    # Ensure multiple errors were reported
    error_lines = [line for line in outputs if "Invalid IP address" in line]
    assert (
        len(error_lines) == 3
    ), "Expected three invalid IP warnings, one for each failed attempt"

    # The operator should indeed be asked to try again each time
    retry_lines = [line for line in outputs if "Please try again" in line]
    assert len(retry_lines) == 3
