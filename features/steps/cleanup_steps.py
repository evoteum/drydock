from behave import given, when, then
import os
import tempfile

# Import your real cleanup logic
from drydock_runner import run_cleanup


@given("a temporary working directory exists")
def step_tmp_dir_exists(context):
    context.tmp_dir = tempfile.mkdtemp(prefix="lab-cleanup-test-")
    assert os.path.isdir(context.tmp_dir)


@when("the cleanup process is executed")
def step_run_cleanup(context):
    context.cleanup_result = None

    try:
        context.cleanup_result = run_cleanup(context.tmp_dir)
    except Exception as exc:
        context.cleanup_exception = exc


@then("the temporary directory is removed")
def step_tmp_dir_removed(context):
    assert not os.path.exists(
        context.tmp_dir
    ), "Cleanup did not remove the temporary working directory."
