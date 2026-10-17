import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str | Path) -> Dict[str, Any]:
    """
    Loads a YAML configuration file.

    Args:
        config_path (str | Path): Path to the YAML file.

    Returns:
        Dict[str, Any]: Configuration dictionary.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
