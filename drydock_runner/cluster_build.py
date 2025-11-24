import os
from drydock_runner.ip_discovery import discover_inaugural_ip
from drydock_runner.environment import (
    EnvironmentValidationError,
)
from drydock_runner.orchestration import (
    run_orchestration,
    OrchestrationResult,
    OrchestrationError,
)
from drydock_runner.kubectl_runner import real_kubectl_apply
from drydock_runner.kubeconfig_fetcher import real_fetch_kubeconfig
from drydock_runner.static_ip_assigner import StaticIPAssigner
import ipaddress


class BootstrapConfigurationError(EnvironmentValidationError):
    pass


class BootstrapResult(OrchestrationResult):
    pass


def run_bootstrap(
    static_ip: str,
    gateway: str,
    cidr: str,
    nameservers: list,
    hostname: str,
    tmp_dir: str,
    ansible_playbook_func=None,
    ansible_install_func=None,
    clone_func=None,
    kubectl_apply_func=real_kubectl_apply,
    node_ip_address=None,
    discovery_func=discover_inaugural_ip,
    static_ip_assigner_func=StaticIPAssigner,
    ssh_user="ubuntu",
    ssh_password="bootstrap",
) -> OrchestrationResult:
    """
    Full bootstrap workflow.
    """

    if clone_func is None:
        raise OrchestrationError("clone_func dependency has not been provided")

    try:
        repos = clone_func()
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
        if node_ip_address is None:
            print("[INFO] No IP supplied. Running automatic discovery...")
            dhcp_ip = discovery_func(cidr=cidr)
            print(f"[INFO] Discovered inaugural node at DHCP IP {dhcp_ip}")
        else:
            dhcp_ip = node_ip_address

        assigner = static_ip_assigner_func(
            ssh_user=ssh_user,
            ssh_password=ssh_password,
        )

        print(f"[INFO] Assigning static IP {static_ip}")

        assigner.assign(
            dhcp_ip=dhcp_ip,
            static_ip=static_ip,
            gateway=gateway,
            nameservers=nameservers,
            hostname=hostname,
            mask=ipaddress.ip_network(cidr, strict=False).prefixlen,
        )

        node_ip_address = static_ip
        print(f"[INFO] Host now reachable at static IP {node_ip_address}")

    except Exception as exc:
        raise OrchestrationError(
            f"Failure during IP discovery or static IP assignment: {exc}"
        ) from exc

    try:
        provision_result = run_orchestration(
            node_ip_address=node_ip_address,
            ansible_func=ansible_playbook_func,
        )
    except Exception as exc:
        raise OrchestrationError(f"Provisioning failed: {exc}") from exc

    try:
        local_kubeconfig_dir = os.path.join(tmp_dir, "kubeconfig")
        os.makedirs(local_kubeconfig_dir, exist_ok=True)
        local_kubeconfig_path = os.path.join(local_kubeconfig_dir, "config")

        real_fetch_kubeconfig(
            machine_ip=node_ip_address,
            local_output_path=local_kubeconfig_path,
        )

        root_app_path = os.path.join(
            config_repo_path, "clusters", "kubernetes-lab", "root-application.yaml"
        )

        if kubectl_apply_func is None:
            raise OrchestrationError(
                "kubectl_apply_func dependency has not been provided"
            )

        kubectl_apply_func(
            kubeconfig_path=local_kubeconfig_path,
            manifest_path=root_app_path,
        )

    except Exception as exc:
        raise OrchestrationError(
            f"Failed to apply ArgoCD root Application: {exc}"
        ) from exc

    provision_result.discovery_warning = False
    provision_result.ip_prompted = True

    return provision_result
