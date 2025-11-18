#!/usr/bin/env python3

import sys
import tempfile

from dotenv import load_dotenv

from bootstrap_runner.kubectl_runner import real_kubectl_apply

from bootstrap_runner.ip_prompt import prompt_for_ip
from bootstrap_runner.clean import run_cleanup, CleanupError
from bootstrap_runner.cluster_build import run_bootstrap
from bootstrap_runner.environment import EnvironmentValidationError
from bootstrap_runner.orchestration import OrchestrationError
from bootstrap_runner.git_runner import clone_required_repositories
from bootstrap_runner.ansible_runner import (
    real_ansible_playbook,
    real_ansible_requirements,
)
from bootstrap_runner.tofu_runner import real_tofu_init, real_tofu_apply
from os import getenv

INDENT = " " * 8


def main():
    """
    Entry point for the Kubernetes lab bootstrap tool.

    Responsibilities:
      1. Create a temporary working directory.
      2. Validate environment configuration and operator input.
      3. Execute tofu stages and Ansible provisioning.
      4. Report success or failure clearly.
      5. Perform cleanup unconditionally.
    """
    load_dotenv()
    tmp_dir = tempfile.mkdtemp(prefix="k8s-lab-bootstrap-")
    print(f"[INFO] Working directory created at: {tmp_dir}")
    print("[INFO] Starting cluster bootstrap process...")
    tofu_config_path = f"{tmp_dir}/tofu/development"

    try:
        result = run_bootstrap(
            tmp_dir=tmp_dir,
            tofu_init_func=lambda: real_tofu_init(
                config_path=tofu_config_path,
                backend_bucket=getenv("TF_BACKEND_BUCKET"),
                backend_region=getenv("TF_BACKEND_REGION"),
                backend_key=getenv("TF_BACKEND_KEY"),
            ),
            tofu_apply_func=lambda: real_tofu_apply(
                config_path=tofu_config_path, dhcp_enabled=True
            ),
            ansible_playbook_func=lambda ip: real_ansible_playbook(
                temporary_dir=tmp_dir, ip_address=ip
            ),
            ansible_install_func=lambda: real_ansible_requirements(
                requirements_path="bootstrap_node_config/requirements.yml"
            ),
            prompt_func=prompt_for_ip,
            clone_func=lambda: clone_required_repositories(base_dir=tmp_dir),
            kubectl_apply_func=real_kubectl_apply,
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
