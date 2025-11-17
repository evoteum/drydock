import traceback


class OrchestrationError(Exception):
    pass


class NetworkDiscoveryError(Exception):
    pass


class OrchestrationResult:
    def __init__(self,
                 success: bool,
                 machine_ip: str = None,
                 error_message: str = None,
                 discovery_warning: bool = False,
                 ip_prompted: bool = False):
        self.success = success
        self.machine_ip = machine_ip
        self.error_message = error_message
        self.discovery_warning = discovery_warning
        self.ip_prompted = ip_prompted


def run_with_discovery(discovery_func, prompt_func):
    """
    Try network discovery. If it fails, prompt for IP.
    Returns an object with machine_ip and discovery_warning.
    """

    class _DiscoveryResult:
        def __init__(self, machine_ip, discovery_warning):
            self.machine_ip = machine_ip
            self.discovery_warning = discovery_warning

    try:
        ip = discovery_func()
        if ip is None:
            raise ValueError("Discovery returned no result")
        return _DiscoveryResult(machine_ip=ip, discovery_warning=False)
    except Exception:
        ip = prompt_func()
        return _DiscoveryResult(machine_ip=ip, discovery_warning=True)


def run_orchestration(
    machine_ip: str,
    discovery_func,
    tofu_init_func,
    tofu_apply_func,
    ansible_func,
    infra_repo_path: str,
    config_repo_path: str
):
    """
    Perform provisioning after IP discovery:

      * tofu init
      * tofu apply
      * ansible playbook run
      (ArgoCD and GitOps handover are separate steps)

    The config_repo_path is required by the Ansible runner so that
    kubeadm, ArgoCD, and values files can be sourced from Git.
    """

    try:
        tofu_init_func(infra_repo_path)
    except Exception as exc:
        raise OrchestrationError(
            f"tofu init failed: {exc}"
        ) from exc

    try:
        tofu_apply_func(infra_repo_path)
    except Exception as exc:
        raise OrchestrationError(
            f"tofu apply failed: {exc}"
        ) from exc

    try:
        ansible_func(
            machine_ip,
            ansible_dir=_find_ansible_dir(),
            config_repo_path=config_repo_path
        )
    except Exception as exc:
        tb = traceback.format_exc()
        raise OrchestrationError(
            f"Ansible execution failed: {exc}\n{tb}"
        ) from exc

    return OrchestrationResult(
        success=True,
        machine_ip=machine_ip,
        discovery_warning=False,
        ip_prompted=True
    )


def _find_ansible_dir():
    """
    Resolve the ansible directory relative to this module.
    """
    import os
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "ansible"
    )