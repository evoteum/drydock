from behave import given, when, then
import os

# Import the real validation function.
# Adjust this import to match your codebase.
from python.environment import validate_ip_address, InvalidIPAddressError


@given("backend configuration is available")
def step_backend_config_available(context):
    # These values only need to exist. The acceptance test does not care what they are.
    os.environ["TF_BACKEND_BUCKET"] = "test-bucket"
    os.environ["TF_BACKEND_KEY"] = "test-key"
    os.environ["TF_BACKEND_REGION"] = "eu-west-2"


@when("I enter an invalid IP address")
def step_enter_invalid_ip(context):
    context.input_ip = "999.999.999.999"  # Deliberately invalid
    try:
        context.ip_validation = validate_ip_address(context.input_ip)
        context.ip_validation_error = None
    except Exception as exc:
        context.ip_validation = None
        context.ip_validation_error = exc


@when("I enter a valid IP address")
def step_enter_valid_ip(context):
    context.input_ip = "192.168.8.50"
    try:
        context.ip_validation = validate_ip_address(context.input_ip)
        context.ip_validation_error = None
    except Exception as exc:
        context.ip_validation = None
        context.ip_validation_error = exc


@then("I am told that the address is invalid")
def step_address_invalid(context):
    assert context.ip_validation_error is not None, (
        "Invalid IP address should have raised an error."
    )
    assert isinstance(context.ip_validation_error, InvalidIPAddressError), (
        "Validation failed, but not with the expected InvalidIPAddressError."
    )


@then("I am prompted to try again")
def step_prompt_try_again(context):
    # For acceptance tests we cannot check user prompts directly.
    # Instead we assert that no valid result was returned.
    assert context.ip_validation is None, (
        "A valid result was returned for an invalid IP address."
    )


@then("the bootstrap continues")
def step_bootstrap_continues(context):
    # Valid IP should pass without error.
    assert context.ip_validation_error is None, (
        f"Validation unexpectedly failed: {context.ip_validation_error}"
    )

    # The function should return a truthy or normalised value.
    assert context.ip_validation is not None, (
        "Validation should return a result for a valid IP address."
    )