from behave import given, when, then
import os

from python.orchestration import run_with_discovery
from python.orchestration import NetworkDiscoveryError


@given("backend configuration is available")
def step_backend_config_available(context):
    os.environ["TF_BACKEND_BUCKET"] = "test-bucket"
    os.environ["TF_BACKEND_KEY"] = "test-key"
    os.environ["TF_BACKEND_REGION"] = "eu-west-2"


@given("the network cannot be scanned")
def step_network_cannot_be_scanned(context):
    # Behave cannot patch directly, so we store a flag on the context.
    # The orchestration layer should accept an injectable discovery function.
    context.force_discovery_failure = True


@when("I run the bootstrap tool")
def step_run_bootstrap(context):
    """
    The orchestration entry point must support dependency injection:
    run_with_discovery(discovery_func=...) so that in tests we can
    simulate discovery failure without touching the real network.
    """

    def failing_discovery():
        raise NetworkDiscoveryError("Network scan failed for testing")

    try:
        if context.force_discovery_failure:
            context.result = run_with_discovery(discovery_func=failing_discovery)
        else:
            context.result = run_with_discovery()
        context.error = None
    except Exception as exc:
        context.result = None
        context.error = exc


@then("I am warned about the scan failure")
def step_warned_about_failure(context):
    # The bootstrap tool should NOT crash, so error must not propagate.
    assert context.error is None, (
        f"Bootstrap crashed instead of warning: {context.error}"
    )

    # The result object should contain a warning flag or message.
    assert hasattr(context.result, "discovery_warning"), (
        "No discovery warning present in bootstrap result."
    )
    assert context.result.discovery_warning is True, (
        "Bootstrap did not mark discovery warning as expected."
    )


@then("I am still able to provide a node IP address manually")
def step_prompt_for_ip_manually(context):
    # The result must indicate that the workflow is still active.
    assert hasattr(context.result, "ip_prompted"), (
        "Bootstrap did not prompt for manual IP after discovery failure."
    )
    assert context.result.ip_prompted is True, (
        "Bootstrap did not allow manual IP entry after discovery failure."
    )
