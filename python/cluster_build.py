import os

from python.environment import validate_environment, EnvironmentValidationError
from python.ip_prompt import get_ip_for_bootstrap
from python.orchestration import (
    run_with_discovery,
    run_orchestration,
    OrchestrationResult,
    OrchestrationError
)
from python.orchestration import NetworkDiscoveryError
from python.kubectl_ops import real_kubectl_apply


def run_bootstrap(
    tmp_dir: str,
    discovery_func=None,
    tofu_init_func=None,
    tofu_apply_func=None,
    ansible_func=None,
    ansible_galaxy_func=None,
    prompt_func=get_ip_for_bootstrap,
    clone_func=None,
    kubectl_apply_func=real_kubectl_apply,
) -> OrchestrationResult:
    """
    Full bootstrap workflow.

    Responsibilities:
      1. Validate environment configuration.
      2. Clone required Git repositories (infrastructure and config).
      3. Install required Ansible Galaxy roles and collections.
      4. Attempt network discovery.
      5. Prompt operator for an IP address if needed.
      6. Run tofu init and apply.
      7. Run Ansible to install Kubernetes, Cilium, and ArgoCD.
      8. Apply the ArgoCD root Application to hand control to GitOps.
      9. Return success or failure via OrchestrationResult.

    All low level operations are dependency-injected for testability.
    """

    try:
        validate_environment()
    except EnvironmentValidationError as exc:
        raise OrchestrationError(f"Environment validation failed: {exc}") from exc

    if clone_func is None:
        raise OrchestrationError(
            "clone_func dependency has not been provided"
        )

    try:
        repos = clone_func(tmp_dir)
        infra_repo_path = repos["infrastructure"]
        config_repo_path = repos["config"]
    except Exception as exc:
        raise OrchestrationError(
            f"Failed to clone repositories: {exc}"
        ) from exc

    if ansible_galaxy_func is None:
        raise OrchestrationError(
            "ansible_galaxy_func dependency has not been provided"
        )

    try:
        ansible_galaxy_func(repos["bootstrap"])
    except Exception as exc:
        raise OrchestrationError(
            f"Failed to install Ansible Galaxy requirements: {exc}"
        ) from exc

    try:
        discovery_result = run_with_discovery(
            discovery_func=discovery_func,
            prompt_func=prompt_func
        )
    except Exception as exc:
        raise OrchestrationError(
            f"Failure during discovery or IP prompt: {exc}"
        ) from exc

    machine_ip = discovery_result.machine_ip

    try:
        provision_result = run_orchestration(
            machine_ip=machine_ip,
            discovery_func=discovery_func,
            tofu_init_func=tofu_init_func,
            tofu_apply_func=tofu_apply_func,
            ansible_func=ansible_func,
            infra_repo_path=infra_repo_path,
            config_repo_path=config_repo_path,
        )
    except Exception as exc:
        raise OrchestrationError(
            f"Provisioning failed: {exc}"
        ) from exc

    try:
        kubeconfig_path = "/home/ubuntu/.kube/config"

        root_app_path = os.path.join(
            config_repo_path,
            "clusters",
            "kubernetes-lab",
            "root-application.yaml"
        )

        if kubectl_apply_func is None:
            raise OrchestrationError(
                "kubectl_apply_func dependency has not been provided"
            )

        kubectl_apply_func(kubeconfig_path, root_app_path)

    except Exception as exc:
        raise OrchestrationError(
            f"Failed to apply ArgoCD root Application: {exc}"
        ) from exc

    provision_result.discovery_warning = discovery_result.discovery_warning
    provision_result.ip_prompted = True

    return provision_result