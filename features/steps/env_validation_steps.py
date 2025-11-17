from behave import given, when, then
import os
from python.cluster_build import run_bootstrap, BootstrapConfigurationError


@given("required backend configuration is not available")
def step_missing_backend_config(context):
    # Ensure all relevant variables are removed
    for var in ["TF_BACKEND_BUCKET", "TF_BACKEND_KEY", "TF_BACKEND_REGION"]:
        if var in os.environ:
            del os.environ[var]


@when("I run the bootstrap tool")
def step_run_bootstrap_missing_config(context):
    try:
        context.bootstrap_result = run_bootstrap(
            tmp_dir="/tmp/bootstrap-test",
            machine_ip="192.168.8.50"
        )
        context.bootstrap_exception = None
    except Exception as exc:
        context.bootstrap_result = None
        context.bootstrap_exception = exc


@then("I am informed that configuration is missing")
def step_informed_config_missing(context):
    assert context.bootstrap_exception is not None, (
        "Bootstrap should have failed due to missing configuration."
    )

    assert isinstance(context.bootstrap_exception, BootstrapConfigurationError), (
        "Bootstrap failed, but not with a configuration error."
    )


@then("the bootstrap process does not start")
def step_bootstrap_not_started(context):
    # If the bootstrap owns side effects (DHCP, cloning, tofu, ansible),
    # we assert here that none of that happened.
    # Simplest acceptance-level assertion:
    assert context.bootstrap_result is None, (
        "Bootstrap result should be None when configuration is invalid."
    )