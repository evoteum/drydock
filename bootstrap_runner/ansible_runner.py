import subprocess
import os
import pathlib
import json


class AnsibleExecutionError(Exception):
    pass


class AnsibleRequirementsError(Exception):
    pass


def real_ansible_requirements(
    requirements_path: str = "bootstrap_node_config/requirements.yml",
) -> None:
    """
    Install Ansible collection and role requirements from a requirements.yaml file.

    The function validates that ansible-galaxy exists,
    checks that the file exists,
    and raises a clear exception if installation fails.
    """
    requirements_path_normalised = pathlib.Path(requirements_path)

    if not requirements_path_normalised.exists():
        raise AnsibleRequirementsError(
            f"Requirements file not found: {requirements_path_normalised}"
        )

    # Check the ansible-galaxy command is available
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

    # Install collections
    collection_res = subprocess.run(
        [
            "ansible-galaxy",
            "collection",
            "install",
            "-r",
            str(requirements_path_normalised),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if collection_res.returncode != 0:
        raise AnsibleRequirementsError(
            f"Collection installation failed:\n{collection_res.stderr}"
        )

    # Install roles
    role_res = subprocess.run(
        ["ansible-galaxy", "role", "install", "-r", str(requirements_path_normalised)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if role_res.returncode != 0:
        raise AnsibleRequirementsError(f"Role installation failed:\n{role_res.stderr}")


#
# Your playbook expects:
#
# kubeadm_config_src
# argocd_manifest
# argocd_values
#
# But your real_ansible_playbook() currently does not pass these.
# extra_vars = {
#     "kubeadm_config_src": f"{config_repo_path}/config/kubeadm/kubeadm-config.yaml",
#     "argocd_manifest": f"{config_repo_path}/config/apps.yaml",
# }


def real_ansible_playbook(
    ip_address: str = None,
    ansible_dir: str = "bootstrap_node_config",
    temporary_dir: str = None,
) -> None:
    """
    Run the Ansible playbook on the given IP address, passing in the
    correct configuration paths required for kubeadm init, Cilium,
    and ArgoCD installation.

    This function is dependency-injected into the bootstrap workflow so it
    can be replaced with a mock in tests.
    """

    playbook_file = os.path.join(ansible_dir, "playbook.yaml")
    if not os.path.exists(playbook_file):
        raise AnsibleExecutionError(f"playbook.yaml not found in: {ansible_dir}")

    inventory = (
        f"{ip_address} "
        f"ansible_user=ubuntu "
        f"ansible_ssh_pass=bootstrap "
        f"ansible_python_interpreter=/usr/bin/python3,"
    )

    kubeadm_config_src = os.path.join(
        temporary_dir,
        "kubernetes-lab-config",
        "clusters",
        "kubernetes-lab",
        "kubeadm-controlplane-config.yaml",
    )

    argocd_manifest = os.path.join(
        temporary_dir,
        "kubernetes-lab-config",
        "clusters",
        "kubernetes-lab",
        "argocd-install.yaml",
    )

    argocd_values = os.path.join(
        temporary_dir, "kubernetes-lab-config", "values", "argocd.yaml"
    )

    for required_file in [kubeadm_config_src, argocd_manifest, argocd_values]:
        if not os.path.exists(required_file):
            raise AnsibleExecutionError(
                f"Required configuration file missing: {required_file}"
            )

    extra_vars = [
        f"kubeadm_config_src={kubeadm_config_src}",
        f"argocd_manifest={argocd_manifest}",
        f"argocd_values={argocd_values}",
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
