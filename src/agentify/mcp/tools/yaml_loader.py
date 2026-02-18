import os
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any

def load_yaml_tools(path: str) -> List[Tuple[Path, Dict[str, Any]]]:
    """
    Load YAML tool definitions from a file or directory.

    Args:
        path: Path to a single YAML file or a directory containing YAML files.

    Returns:
        List of tuples: (Path to YAML file, parsed dict)
    """
    tools = []
    path = Path(path).resolve()

    if path.is_file() and path.suffix in (".yaml", ".yml"):
        with open(path, "r") as f:
            tools.append((path, yaml.safe_load(f)))

    elif path.is_dir():
        for file in path.iterdir():
            if file.suffix in (".yaml", ".yml"):
                with open(file, "r") as f:
                    tools.append((file, yaml.safe_load(f)))
    else:
        raise ValueError(f"Invalid path: {path}")

    return tools
