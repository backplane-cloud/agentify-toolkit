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




