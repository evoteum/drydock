import subprocess
import os

class AnsibleExecutionError(Exception):
    pass


def real_ansible_runner(
    ip_address: str,
    ansible_dir: str,
    config_repo_path: str,
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
        raise AnsibleExecutionError(
            f"playbook.yaml not found in: {ansible_dir}"
        )

    inventory = (
        f"{ip_address} "
        f"ansible_user=ubuntu "
        f"ansible_ssh_pass=bootstrap "
        f"ansible_python_interpreter=/usr/bin/python3,"
    )

    kubeadm_config_src = os.path.join(
        config_repo_path,
        "clusters",
        "kubernetes-lab",
        "kubeadm-controlplane-config.yaml"
    )

    argocd_manifest = os.path.join(
        config_repo_path,
        "clusters",
        "kubernetes-lab",
        "argocd-install.yaml"
    )

    argocd_values = os.path.join(
        config_repo_path,
        "values",
        "argocd.yaml"
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
                "-i", inventory,
                playbook_file,
                *extra_vars_args,
            ],
            check=True,
            cwd=ansible_dir
        )
    except subprocess.CalledProcessError as exc:
        raise AnsibleExecutionError(
            f"ansible-playbook execution failed: {exc}"
        ) from exc
