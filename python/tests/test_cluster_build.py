import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from python.cluster_build import (
    run_bootstrap,
    BootstrapConfigurationError,
    BootstrapResult
)


def make_env_valid():
    """Helper to set valid backend configuration."""
    os.environ["TF_BACKEND_BUCKET"] = "test-bucket"
    os.environ["TF_BACKEND_KEY"] = "test-key"
    os.environ["TF_BACKEND_REGION"] = "eu-west-2"


def clear_env():
    """Helper to remove backend configuration variables."""
    for var in ["TF_BACKEND_BUCKET", "TF_BACKEND_KEY", "TF_BACKEND_REGION"]:
        if var in os.environ:
            del os.environ[var]


@patch("python.cluster_build.tofu_init_func")
@patch("python.cluster_build.tofu_apply_func")
@patch("python.cluster_build.ansible_func")
@patch("python.cluster_build.discovery_func")
def test_bootstrap_runs_successfully(
    mock_discovery,
    mock_ansible,
    mock_apply,
    mock_init
):
    """
    A successful bootstrap should:
    1. Validate environment configuration.
    2. Perform network discovery.
    3. Initialise tofu.
    4. Apply tofu to enable DHCP or related provisioning.
    5. Run the Ansible playbook.
    6. Return a BootstrapResult with success=True.

    This test keeps the engineer sane and avoids having to
    provision Tinkerbell, Ansible and tofu in a unit test.
    """

    make_env_valid()

    # Mock behaviours for a happy path
    mock_discovery.return_value = True
    mock_init.return_value = True
    mock_apply.return_value = True
    mock_ansible.return_value = True

    tmp_dir = tempfile.mkdtemp(prefix="cluster-build-test-")
    machine_ip = "192.168.8.50"

    result = run_bootstrap(
        tmp_dir=tmp_dir,
        machine_ip=machine_ip,
        discovery_func=mock_discovery,
        ansible_func=mock_ansible,
        tofu_init_func=mock_init,
        tofu_apply_func=mock_apply
    )

    assert isinstance(result, BootstrapResult)
    assert result.success is True

    # Ensure each stage was called once
    mock_discovery.assert_called_once()
    mock_init.assert_called_once()
    mock_apply.assert_called_once()
    mock_ansible.assert_called_once()


def test_bootstrap_fails_on_missing_environment():
    """
    If required backend configuration is missing, bootstrap must fail
    immediately with BootstrapConfigurationError. The orchestration must
    not attempt tofu, discovery or Ansible.
    """

    clear_env()

    tmp_dir = "/tmp/cluster-build-test"
    machine_ip = "192.168.8.50"

    with pytest.raises(BootstrapConfigurationError):
        run_bootstrap(tmp_dir=tmp_dir, machine_ip=machine_ip)


@patch("python.cluster_build.discovery_func")
def test_bootstrap_handles_discovery_failure(mock_discovery):
    """
    A failure in network discovery should be captured and reported,
    but bootstrap should still prompt the user for a manual IP address.

    The returned BootstrapResult should contain discovery_warning=True.
    """

    make_env_valid()

    # Mock a failure
    mock_discovery.side_effect = Exception("Discovery exploded elegantly")

    tmp_dir = tempfile.mkdtemp(prefix="cluster-build-test-fail-")
    machine_ip = "192.168.8.50"

    result = run_bootstrap(
        tmp_dir=tmp_dir,
        machine_ip=machine_ip,
        discovery_func=mock_discovery
    )

    assert isinstance(result, BootstrapResult)
    assert result.success is True, "Bootstrap should continue gracefully."
    assert result.discovery_warning is True, "Expected discovery warning flag."
    assert result.ip_prompted is True, "Bootstrapping should still prompt operator for IP."


@patch("python.cluster_build.ansible_func")
def test_bootstrap_reports_ansible_failure(mock_ansible):
    """
    If the Ansible run fails, bootstrap should surface the failure
    cleanly and return success=False instead of crashing.
    """

    make_env_valid()

    # Happy mocks for early stages
    fake_ok = MagicMock(return_value=True)

    # Ansible fails
    mock_ansible.side_effect = Exception("Ansible has found a new and exciting way to fail")

    tmp_dir = tempfile.mkdtemp(prefix="cluster-build-test-ansible-")
    machine_ip = "192.168.8.50"

    result = run_bootstrap(
        tmp_dir=tmp_dir,
        machine_ip=machine_ip,
        discovery_func=fake_ok,
        tofu_init_func=fake_ok,
        tofu_apply_func=fake_ok,
        ansible_func=mock_ansible
    )

    assert isinstance(result, BootstrapResult)
    assert result.success is False, "Bootstrap should fail cleanly when Ansible fails."
    assert result.error_message is not None, "Failure should include a useful error message."