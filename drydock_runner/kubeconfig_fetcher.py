import subprocess
import os
import stat


class KubeconfigFetchError(Exception):
    pass


def real_fetch_kubeconfig(
    machine_ip: str,
    local_output_path: str,
    remote_path: str = "/home/ubuntu/.kube/config",
    user: str = "ubuntu",
    password: str = "bootstrap",
):
    """
    Fetch the kubeconfig from the newly bootstrapped node and store it locally.

    Assumptions:
      - The remote user is 'ubuntu'
      - The temporary bootstrap password is 'bootstrap'
      - The remote kubeconfig path is /home/ubuntu/.kube/config

    This function uses sshpass to avoid interactive prompts. The bootstrap
    design is intentionally short-lived, so password authentication is
    acceptable at this stage.

    The kubeconfig is written with restrictive permissions.
    """

    # Ensure sshpass is installed
    try:
        subprocess.run(
            ["sshpass", "-V"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except FileNotFoundError:
        raise KubeconfigFetchError("sshpass is required but is not installed.")

    parent = os.path.dirname(local_output_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    scp_command = [
        "sshpass",
        "-p",
        password,
        "scp",
        "-o",
        "StrictHostKeyChecking=no",
        f"{user}@{machine_ip}:{remote_path}",
        local_output_path,
    ]

    try:
        subprocess.run(scp_command, check=True)
    except subprocess.CalledProcessError as exc:
        raise KubeconfigFetchError(
            f"Failed to fetch kubeconfig via SCP: {exc}"
        ) from exc

    os.chmod(local_output_path, stat.S_IRUSR | stat.S_IWUSR)
