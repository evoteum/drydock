import os
import subprocess
import tempfile


def clone_repositories(
    repos: dict[str, any], base_dir: str | None = None
) -> dict[str, str]:
    """
    Clone all repositories defined in bootstrapSources.repositories.

    Args:
        repos: Mapping from repository logical name to Repository model.
        base_dir: Optional parent directory where repos should be cloned.

    Returns:
        dict mapping logical repository names -> local checkout path
    """
    if base_dir is None:
        base_dir = tempfile.mkdtemp(prefix="drydock-repos-")

    results = {}

    for name, repo in repos.items():
        repo_path = os.path.join(base_dir, name)
        os.makedirs(repo_path, exist_ok=True)

        print(f"[INFO] Cloning '{name}' from {repo.url} @ {repo.branch}")

        try:
            subprocess.run(
                ["git", "clone", "--branch", repo.branch, repo.url, repo_path],
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Failed to clone repository {name}: {exc}") from exc

        results[name] = repo_path

    return results
