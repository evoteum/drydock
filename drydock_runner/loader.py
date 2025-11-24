import yaml
from pathlib import Path
from .config import BootstrapConfig


def load_config(path: str | Path) -> BootstrapConfig:
    """
    Load and validate the Drydock configuration file.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r") as f:
        raw = yaml.safe_load(f)

    try:
        return BootstrapConfig(**raw)
    except Exception as exc:
        raise ValueError(f"Invalid Drydock configuration: {exc}") from exc
