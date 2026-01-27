# Copyright 2026 Backplane Software
# Licensed under the Apache License, Version 2.0

from pathlib import Path
import yaml
   
def load_agent_specs(agent_dir: Path | str = "agents") -> list[dict]:
    agent_dir = Path(agent_dir)
    specs = []
    for path in agent_dir.glob("*.yaml"):
        with open(path, "r") as f:
            spec = yaml.safe_load(f)
            spec["_file"] = path.name  # optional metadata
            specs.append(spec)
    return specs

def load_tool_specs(tool_dir: Path | str = "tools") -> list[dict]:
    """
    Load tool YAML from a directory and return its spec as a dictionary.
    """
    tool_dir = Path(tool_dir)
    specs = []
    for path in tool_dir.glob("*.yaml"):
        with open(path, "r") as f:
            spec = yaml.safe_load(f)
            spec["_file"] = path.name  # optional metadata
            specs.append(spec)
    return specs

def load_tool_spec(tool_path: Path | str) -> dict:
    """
    Load a single tool YAML file and return its spec as a dictionary.
    """
    tool_path = Path(tool_path)
    with open(tool_path, "r") as f:
        spec = yaml.safe_load(f)
    
    # optional metadata
    spec["_file"] = tool_path.name
    spec["_path"] = str(tool_path)
    
    return spec



