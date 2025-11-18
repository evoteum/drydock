import os
import subprocess
from pathlib import Path


class GitCloneError(Exception):
    pass


def clone_repository(repo_url: str, destination: str) -> None:
    """
    Clone a Git repository into the given destination directory.
    Raises GitCloneError on failure.
    """
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", repo_url, destination],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        raise GitCloneError(
            f"Failed to clone {repo_url} into {destination}: {exc.stderr.decode()}"
        )


def clone_required_repositories(base_dir: str) -> dict:
    """
    Clone all repositories required for cluster bootstrap.

    Returns a dictionary containing paths to cloned repos:
        {
            "infrastructure": "...",
            "config": "..."
        }
    """

    REPOS = {
        "infrastructure": "https://github.com/evoteum/kubernetes-lab-infrastructure.git",
        "config": "https://github.com/evoteum/kubernetes-lab-config.git",
    }

    cloned_paths = {}

    for name, url in REPOS.items():
        destination = os.path.join(base_dir, name)
        Path(destination).mkdir(parents=True, exist_ok=True)

        clone_repository(url, destination)
        cloned_paths[name] = destination

    return cloned_paths
