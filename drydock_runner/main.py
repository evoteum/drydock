#!/usr/bin/env python3

import sys
import tempfile
import argparse
import ipaddress


from drydock_runner.kubectl_runner import real_kubectl_apply
from drydock_runner.clean import run_cleanup, CleanupError
from drydock_runner.cluster_build import run_bootstrap
from drydock_runner.environment import EnvironmentValidationError
from drydock_runner.orchestration import OrchestrationError
from drydock_runner.git_runner import clone_repositories
from drydock_runner.ansible_runner import (
    real_ansible_playbook,
    real_ansible_requirements,
)
from drydock_runner.loader import load_config
from pathlib import Path
import stat
import os

INDENT = " " * 8


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bootstrap the inaugural Kubernetes lab node."
    )

    parser.add_argument(
        "--ip",
        type=str,
        help="IP address of the inaugural Ubuntu host. "
        "If omitted, automatic discovery will be attempted.",
    )
    parser.add_argument(
        "--config",
        default="bootstrap_runner/config.yaml",
        help="Path to the Drydock configuration file",
    )

    return parser.parse_args()


def validate_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def main():
    """
    Entry point for the Kubernetes lab bootstrap tool.

    Responsibilities:
      1. Create a temporary working directory.
      2. Validate environment configuration and operator input.
      3. Execute Ansible provisioning.
      4. Report success or failure clearly.
      5. Perform cleanup unconditionally.
    """

    args = parse_args()
    cfg = load_config(args.config)

    static_ip = cfg.spec.network.staticIP.address
    gateway = cfg.spec.network.staticIP.gateway
    cidr = cfg.spec.network.cidr
    nameservers = cfg.spec.network.staticIP.nameservers
    hostname = cfg.spec.inauguralNode.hostname

    discovery_settings = cfg.spec.discovery
    inaugural_node = cfg.spec.inauguralNode

    if os.stat(args.config).st_mode & stat.S_IWOTH:
        raise EnvironmentValidationError("Config file must not be world-writable.")

    bootstrap_settings = cfg.spec.bootstrapSources

    if args.ip:
        if not validate_ip(args.ip):
            raise ValueError(f"Invalid IP address: {args.ip}")
        machine_ip = args.ip
        print(f"[INFO] Using user-specified IP: {machine_ip}")
    else:
        print("[INFO] No IP provided. Beginning automatic discovery...")

    tmp_dir = tempfile.mkdtemp(prefix="k8s-lab-bootstrap-")
    print(f"[INFO] Working directory created at: {tmp_dir}")
    print("[INFO] Starting cluster bootstrap process...")

    config_repo_path = Path(tmp_dir) / "config"
    config_paths = cfg.spec.bootstrapSources.repositories["config"].paths

    kubeadm_config_path = (config_repo_path / config_paths.kubeadmConfig).as_posix()
    argocd_manifest_path = (config_repo_path / config_paths.argocdManifest).as_posix()
    argocd_values_path = (config_repo_path / config_paths.argocdValues).as_posix()

    try:
        result = run_bootstrap(
            static_ip=static_ip,
            cidr=cidr,
            gateway=gateway,
            nameservers=nameservers,
            hostname=hostname,
            tmp_dir=tmp_dir,
            ansible_playbook_func=lambda ip: real_ansible_playbook(
                ip_address=ip,
                kubeadm_config_src=kubeadm_config_path,
                argocd_manifest=argocd_manifest_path,
                argocd_values=argocd_values_path,
            ),
            ansible_install_func=lambda: real_ansible_requirements(
                requirements_path="bootstrap_node_config/requirements.yml"
            ),
            clone_func=lambda: clone_repositories(
                repos=bootstrap_settings.repositories,
                base_dir=tmp_dir,
            ),
            kubectl_apply_func=real_kubectl_apply,
            node_ip_address=args.ip,
        )

        if result.success:
            print("[SUCCESS] Cluster bootstrapped successfully.")
            if result.machine_ip:
                print(f"[INFO] Node IP address: {result.machine_ip}")
            return 0

        print("[ERROR] Cluster bootstrap failed.")
        if result.error_message:
            print(f"{INDENT}{str(result.error_message)}")
        return 1

    except EnvironmentValidationError as exc:
        print("[ERROR] Environment configuration is invalid:")
        print(f"{INDENT}{str(exc)}")
        return 2

    except OrchestrationError as exc:
        print("[ERROR] Orchestration error:")
        print(f"{INDENT}{str(exc)}")
        return 3

    finally:
        try:
            run_cleanup(tmp_dir)
            print("[INFO] Temporary directory cleaned.")
        except CleanupError as exc:
            print("[ERROR] Cleanup failed:")
            print(f"{INDENT}{str(exc)}")


if __name__ == "__main__":
    sys.exit(main())
