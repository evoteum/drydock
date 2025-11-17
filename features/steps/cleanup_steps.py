from behave import given, when, then
import os
import shutil
import tempfile

# Import your real cleanup logic
from python.clean import run_cleanup


@given("a temporary working directory exists")
def step_tmp_dir_exists(context):
    # Behave gives each scenario its own context.
    # We create a directory that cleanup should remove.
    context.tmp_dir = tempfile.mkdtemp(prefix="lab-cleanup-test-")
    assert os.path.isdir(context.tmp_dir)


@given("DHCP or provisioning state exists inside the temporary directory")
def step_state_exists(context):
    # We create a fake directory structure to simulate what the cleanup logic expects.
    # Nothing secret or infrastructure-specific. Just enough for testing.
    tofu_path = os.path.join(context.tmp_dir, "tofu", "development")
    os.makedirs(tofu_path, exist_ok=True)

    # Drop a file so the test can verify cleanup behaviour.
    dummy_state = os.path.join(tofu_path, "state.tf")
    with open(dummy_state, "w", encoding="utf8") as f:
        f.write("placeholder")

    context.state_file = dummy_state
    assert os.path.isfile(dummy_state)


@when("the cleanup process is executed")
def step_run_cleanup(context):
    # Call your real cleanup logic.
    # Because the real tool performs subprocess calls (tofu apply etc),
    # your cleanup should be mocked in unit tests, but here in BDD you run the high level call.
    # This keeps behaviour tests stable and focused on orchestration.
    context.cleanup_result = None

    try:
        context.cleanup_result = run_cleanup(context.tmp_dir)
    except Exception as exc:
        # Behave context gets the exception so assertions can check failures.
        context.cleanup_exception = exc


@then("the temporary directory is removed")
def step_tmp_dir_removed(context):
    assert not os.path.exists(context.tmp_dir), (
        "Cleanup did not remove the temporary working directory."
    )


@then("no provisioning or DHCP artefacts remain")
def step_no_state_remains(context):
    # The file and directory structure created earlier should no longer exist.
    assert not os.path.exists(context.state_file), (
        "State file still exists after cleanup."
    )

    # The parent directory should also be gone unless your cleanup logic preserves it deliberately.
    tofu_root = os.path.dirname(os.path.dirname(context.state_file))
    assert not os.path.exists(tofu_root), (
        "Provisioning directory still exists after cleanup."
    )