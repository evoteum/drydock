import subprocess
import os
import pathlib


class AnsibleExecutionError(Exception):
    pass


class AnsibleRequirementsError(Exception):
    pass


def real_ansible_requirements(
    requirements_path: str = "bootstrap_node_config/requirements.yml",
) -> None:

    requirements_path_normalised = pathlib.Path(requirements_path)

    if not requirements_path_normalised.exists():
        raise AnsibleRequirementsError(
            f"Requirements file not found: {requirements_path_normalised}"
        )

    try:
        subprocess.run(
            ["ansible-galaxy", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception as exc:
        raise AnsibleRequirementsError(
            "ansible-galaxy is not available or failed to execute"
        ) from exc

    result = subprocess.run(
        ["ansible-galaxy", "install", "-r", str(requirements_path_normalised)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise AnsibleRequirementsError(
            f"Ansible requirements installation failed:\n{result.stderr}"
        )


def real_ansible_playbook(
    kubeadm_config_src: str,
    argocd_manifest: str,
    argocd_values: str,
    ip_address: str = None,
    ansible_dir: str = "bootstrap_node_config",
) -> None:
    """
    Run the Ansible playbook on the given IP address, passing in the
    correct configuration paths required for kubeadm init, Cilium,
    and ArgoCD installation.

    This function is dependency-injected into the bootstrap workflow so it
    can be replaced with a mock in tests.
    """
    if ip_address is None:
        raise AnsibleRequirementsError("ip_address is required")

    playbook_file = pathlib.Path(ansible_dir) / "playbook.yaml"
    playbook_file = playbook_file.resolve()
    if not os.path.exists(playbook_file):
        raise AnsibleExecutionError(f"playbook.yaml not found in: {ansible_dir}")

    inventory = f"{ip_address},"

    for required_file in [kubeadm_config_src, argocd_manifest, argocd_values]:
        if not os.path.exists(required_file):
            raise AnsibleExecutionError(
                f"Required configuration file missing: {required_file}"
            )

    extra_vars = [
        f"kubeadm_config_src={kubeadm_config_src}",
        f"argocd_manifest={argocd_manifest}",
        f"argocd_values={argocd_values}",
        "ansible_user=ubuntu",
        "ansible_ssh_pass=bootstrap",
    ]

    extra_vars_args = []
    for var in extra_vars:
        extra_vars_args.extend(["--extra-vars", var])

    try:
        subprocess.run(
            [
                "ansible-playbook",
                "-i",
                inventory,
                playbook_file,
                *extra_vars_args,
            ],
            check=True,
            cwd=ansible_dir,
        )
    except subprocess.CalledProcessError as exc:
        raise AnsibleExecutionError(
            f"ansible-playbook execution failed: {exc}"
        ) from exc
