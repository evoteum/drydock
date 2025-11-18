import tempfile
import pathlib
import pytest
from unittest import mock


def test_missing_requirements_file():
    with pytest.raises(AnsibleRequirementsError):
        install_ansible_requirements("does_not_exist.yaml")


def test_runs_when_ansible_galaxy_available():
    # Create a temporary empty file
    with tempfile.TemporaryDirectory() as tmp:
        req = pathlib.Path(tmp) / "requirements.yaml"
        req.write_text("collections: []\nroles: []\n")

        # Mock subprocess.run so we do not call real ansible-galaxy
        with mock.patch("subprocess.run") as run_mock:
            run_mock.return_value = mock.Mock(returncode=0, stdout="", stderr="")
            install_ansible_requirements(str(req))

            # Ensure ansible-galaxy was invoked three times
            assert run_mock.call_count == 3


def test_fails_when_ansible_galaxy_errors():
    with tempfile.TemporaryDirectory() as tmp:
        req = pathlib.Path(tmp) / "requirements.yaml"
        req.write_text("collections: []\nroles: []\n")

        with mock.patch("subprocess.run") as run_mock:
            # First call: ansible-galaxy --version succeeds
            run_mock.side_effect = [
                mock.Mock(returncode=0, stdout="", stderr=""),
                mock.Mock(returncode=1, stdout="", stderr="broken"),
            ]

            with pytest.raises(AnsibleRequirementsError):
                install_ansible_requirements(str(req))
