from behave import given, when, then
import os
import tempfile

# Import the real bootstrap orchestration function.
from drydock_runner import run_bootstrap


@given("valid environment configuration")
def step_valid_env(context):
    # Acceptance tests should not care about low level details.
    # We simply ensure the environment variables your tool expects exist.
    os.environ["TF_BACKEND_BUCKET"] = "bootstrap-test-bucket"
    os.environ["TF_BACKEND_KEY"] = "bootstrap-test-key"
    os.environ["TF_BACKEND_REGION"] = "eu-west-2"


@given("a new machine is available on the network")
def step_machine_available(context):
    # For acceptance tests we do not attempt to simulate real network state.
    # Instead we supply the IP address that the bootstrap workflow would receive.
    context.machine_ip = "192.168.8.50"


@when("the operator runs the bootstrap tool")
def step_run_bootstrap(context):
    # The bootstrap tool usually needs a workspace.
    # Behave scenarios should work in isolated temporary directories.
    context.tmp_dir = tempfile.mkdtemp(prefix="bootstrap-e2e-")

    # The run_bootstrap call should encapsulate the full workflow.
    # The behaviour test asserts only the top level result, not the internal calls.
    try:
        context.bootstrap_result = run_bootstrap(
            tmp_dir=context.tmp_dir, machine_ip=context.machine_ip
        )
    except Exception as exc:
        context.bootstrap_exception = exc


@then("the cluster is ready for GitOps takeover")
def step_cluster_ready(context):
    # A real acceptance test checks observable success criteria.
    # The bootstrap_result object should have a clear success indicator.
    assert (
        hasattr(context, "bootstrap_exception") is False
    ), f"Bootstrap failed with exception: {context.bootstrap_exception}"

    assert context.bootstrap_result is not None, "Bootstrap tool returned no result."

    # The result object should indicate success in a stable, intentional way.
    # Adjust this depending on your actual return type or status model.
    assert (
        context.bootstrap_result.success is True
    ), "Bootstrap tool did not report success."
