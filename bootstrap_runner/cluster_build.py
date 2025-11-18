import os

from bootstrap_runner.environment import (
    validate_environment,
    EnvironmentValidationError,
)
from bootstrap_runner.ip_prompt import prompt_for_ip
from bootstrap_runner.orchestration import (
    run_orchestration,
    OrchestrationResult,
    OrchestrationError,
)
from bootstrap_runner.kubectl_runner import real_kubectl_apply


def run_bootstrap(
    tmp_dir: str,
    tofu_init_func=None,
    tofu_apply_func=None,
    ansible_playbook_func=None,
    ansible_install_func=None,
    prompt_func=prompt_for_ip,
    clone_func=None,
    kubectl_apply_func=real_kubectl_apply,
) -> OrchestrationResult:
    """
    Full bootstrap workflow.
    """

    try:
        validate_environment()
    except EnvironmentValidationError as exc:
        raise OrchestrationError(f"Environment validation failed: {exc}") from exc

    if clone_func is None:
        raise OrchestrationError("clone_func dependency has not been provided")

    try:
        repos = clone_func()
        infra_repo_path = repos["infrastructure"]
        config_repo_path = repos["config"]
    except Exception as exc:
        raise OrchestrationError(f"Failed to clone repositories: {exc}") from exc

    if ansible_install_func is None:
        raise OrchestrationError(
            "ansible_install_func dependency has not been provided"
        )

    try:
        ansible_install_func()
    except Exception as exc:
        raise OrchestrationError(
            f"Failed to install Ansible Galaxy requirements: {exc}"
        ) from exc

    try:
        machine_ip = str(prompt_func())
    except Exception as exc:
        raise OrchestrationError(f"Failure during IP prompt: {exc}") from exc

    try:
        provision_result = run_orchestration(
            machine_ip=machine_ip,
            tofu_init_func=tofu_init_func,
            tofu_apply_func=tofu_apply_func,
            ansible_func=ansible_playbook_func,
        )
    except Exception as exc:
        raise OrchestrationError(f"Provisioning failed: {exc}") from exc

    try:
        kubeconfig_path = "/home/ubuntu/.kube/config"
        root_app_path = os.path.join(
            config_repo_path, "clusters", "kubernetes-lab", "root-application.yaml"
        )

        if kubectl_apply_func is None:
            raise OrchestrationError(
                "kubectl_apply_func dependency has not been provided"
            )

        kubectl_apply_func(kubeconfig_path=kubeconfig_path, manifest_path=root_app_path)

    except Exception as exc:
        raise OrchestrationError(
            f"Failed to apply ArgoCD root Application: {exc}"
        ) from exc

    provision_result.discovery_warning = False
    provision_result.ip_prompted = True

    return provision_result
