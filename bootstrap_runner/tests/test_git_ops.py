import os
import pytest
from bootstrap_runner.git_runner import (
    clone_required_repositories,
    clone_repository,
    GitCloneError,
)


def test_clone_repository_success(monkeypatch, tmp_path):
    def mock_run(cmd, check, stdout, stderr):
        return None

    monkeypatch.setattr("subprocess.run", mock_run)

    dest = tmp_path / "repo"
    clone_repository("https://example.com/repo.git", str(dest))

    assert dest.exists()


def test_clone_repository_failure(monkeypatch, tmp_path):
    def mock_run(cmd, check, stdout, stderr):
        raise subprocess.CalledProcessError(
            returncode=1, cmd=cmd, stderr=b"fatal: repository not found"
        )

    monkeypatch.setattr("subprocess.run", mock_run)

    with pytest.raises(GitCloneError):
        clone_repository("https://example.com/invalid.git", str(tmp_path))


def test_clone_required_repositories(monkeypatch, tmp_path):
    def mock_clone(url, dest):
        Path(dest).mkdir(parents=True)

    monkeypatch.setattr("python.git_ops.clone_repository", mock_clone)

    paths = clone_required_repositories(str(tmp_path))

    assert "infrastructure" in paths
    assert "config" in paths
    assert os.path.isdir(paths["infrastructure"])
    assert os.path.isdir(paths["config"])
