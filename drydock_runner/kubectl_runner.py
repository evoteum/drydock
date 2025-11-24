import subprocess
import os


class KubectlApplyError(Exception):
    pass


def real_kubectl_apply(kubeconfig_path: str = None, manifest_path: str = None) -> None:
    """
    Apply a Kubernetes manifest using kubectl.

    This function is dependency-injected so that tests can supply
    a fake or no-op implementation.

    kubeconfig_path: path to the kubeconfig file created by kubeadm init
    manifest_path: path to a file or directory containing Kubernetes manifests
    """

    if not os.path.exists(manifest_path):
        raise KubectlApplyError(f"Manifest path not found: {manifest_path}")

    try:
        subprocess.run(
            [
                "kubectl",
                "--kubeconfig",
                kubeconfig_path,
                "apply",
                "-f",
                manifest_path,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise KubectlApplyError(f"kubectl apply failed: {exc}") from exc
