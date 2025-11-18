import pytest
from unittest.mock import MagicMock

from bootstrap_runner.orchestration import (
    run_orchestration,
    run_orchestration_with_env_validation,
    OrchestrationResult,
    NetworkDiscoveryError,
)
from bootstrap_runner.environment import EnvironmentValidationError

# ---------------------------------------------------------------------------
# Tests for run_orchestration (provisioning)
# ---------------------------------------------------------------------------


def test_run_orchestration_happy_path():
    fake_init = MagicMock(return_value=True)
    fake_apply = MagicMock(return_value=True)
    fake_ansible = MagicMock(return_value=True)

    result = run_orchestration(
        machine_ip="192.168.8.50",
        tofu_init_func=fake_init,
        tofu_apply_func=fake_apply,
        ansible_func=fake_ansible,
    )

    assert result.success is True
    assert result.error_message is None


def test_run_orchestration_ansible_failure():
    fake_fn = MagicMock(return_value=True)
    fake_ansible = MagicMock(side_effect=Exception("ansible error"))

    result = run_orchestration(
        machine_ip="192.168.8.50",
        tofu_init_func=fake_fn,
        tofu_apply_func=fake_fn,
        ansible_func=fake_ansible,
    )

    assert result.success is False
    assert "ansible error" in result.error_message


def test_run_orchestration_tofu_failures():
    fake_apply = MagicMock(return_value=True)
    fake_ansible = MagicMock(return_value=True)

    fake_init_fail = MagicMock(side_effect=Exception("init failed"))
    fake_apply_fail = MagicMock(side_effect=Exception("apply failed"))

    # Tofu init failure
    result_init = run_orchestration(
        machine_ip="192.168.8.50",
        tofu_init_func=fake_init_fail,
        tofu_apply_func=fake_apply,
        ansible_func=fake_ansible,
    )
    assert result_init.success is False
    assert "init failed" in result_init.error_message

    # Tofu apply failure
    result_apply = run_orchestration(
        machine_ip="192.168.8.50",
        tofu_init_func=fake_discovery,
        tofu_apply_func=fake_apply_fail,
        ansible_func=fake_ansible,
    )
    assert result_apply.success is False
    assert "apply failed" in result_apply.error_message


# ---------------------------------------------------------------------------
# Tests for top-level orchestration with environment validation
# ---------------------------------------------------------------------------


def test_run_orchestration_with_env_validation_missing_env(monkeypatch):
    """Missing backend configuration should raise EnvironmentValidationError."""

    monkeypatch.delenv("TF_BACKEND_BUCKET", raising=False)
    monkeypatch.delenv("TF_BACKEND_KEY", raising=False)
    monkeypatch.delenv("TF_BACKEND_REGION", raising=False)

    with pytest.raises(EnvironmentValidationError):
        run_orchestration_with_env_validation("/tmp/irrelevant")


def test_run_orchestration_with_env_validation_success(monkeypatch):
    """Full orchestration succeeds with valid environment variables."""

    monkeypatch.setenv("TF_BACKEND_BUCKET", "bucket")
    monkeypatch.setenv("TF_BACKEND_KEY", "key")
    monkeypatch.setenv("TF_BACKEND_REGION", "eu-west-2")

    fake_prompt = MagicMock(return_value="192.168.8.50")
    fake_tofu_init = MagicMock(return_value=True)
    fake_tofu_apply = MagicMock(return_value=True)
    fake_ansible = MagicMock(return_value=True)

    result = run_orchestration_with_env_validation(
        tmp_dir="/tmp/irrelevant",
        discovery_func=fake_discovery,
        tofu_init_func=fake_tofu_init,
        tofu_apply_func=fake_tofu_apply,
        ansible_func=fake_ansible,
        prompt_func=fake_prompt,
    )

    assert result.success is True
    assert result.machine_ip == "192.168.8.50"
