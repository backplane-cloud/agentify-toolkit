"""
Copyright 2026 Backplane Software
Licensed under the Apache License, Version 2.0
Author: Lewis Sheridan
Description: Agentify class to build multi-model AI Agents
"""

from dataclasses import dataclass, field
from typing import Optional
import requests

@dataclass
class Action:
    name: str
    method: str
    path: str
    params: dict = field(default_factory=dict)
    
    def to_schema(self) -> dict:
        return {
            "name": self.name,
            "method": self.method,
            "path": self.path,
            "params": self.params or {}
        }

    
@dataclass
class Tool:
    name: str
    description: str
    vendor: str
    type: str   # "internal" or "remote"
    module: Optional[str] = None # for internal
    function: Optional[str] = None # for internal
    endpoint: Optional[str] = None # for remote
    version: Optional[str] = field(default="0.0.0")
    actions: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)


    def to_schema(self) -> dict:
        base = {
            "name": self.name,
            "description": self.description or f"Tool {self.name}",
        }

        # Internal tool → params
        if self.type == "internal":
            base["params"] = self.params or {}
            return base

        # Remote tool → actions
        base["actions"] = [
            action.to_schema()
            for action in self.actions.values()
        ]
        return base

    def invoke(self, action_name: Optional[str] = None, args: dict = None):
        args = args or {}

        # Internal Tool
        if self.type == "internal":
            if not self.module or not self.function:
                raise RuntimeError(f"Internal tool '{self.name}' missing module/function info")

            import importlib
            import sys
            from pathlib import Path

            # TEMPORARY ASSUMPTION:
            # agentify is run as: agentify run examples/solution/internal_demo.yaml
            # so tools live in examples/solution/tools/
            agent_root = Path("examples/solution").resolve()

            if str(agent_root) not in sys.path:
                sys.path.insert(0, str(agent_root))

            module = importlib.import_module(self.module)  # tools.add_numbers
            func = getattr(module, self.function)
            return func(**args)

        # Remote Tool
        if not action_name:
            raise ValueError(f"Action name required for remote tool '{self.name}'")

        # find action
        action = self.actions.get(action_name)
        if not action:
            raise ValueError(f"Unknown action '{action_name}' for tool '{self.name}'")

        # build URL and route based on action.method
        url = f"{self.endpoint}{action.path}"
        method = action.method.upper()

        if method == "GET":
            r = requests.get(url, params=args)
        elif method == "POST":
            r = requests.post(url, json=args)
        elif method == "PUT":
            r = requests.put(url, json=args)
        elif method == "DELETE":
            r = requests.delete(url, json=args)
        else:
            raise ValueError(f"Unsupported HTTP method '{method}'")

        # basic error handling
        if r.status_code >= 400:
            return {
                "error": True,
                "status": r.status_code,
                "response": r.text
            }

        # assume JSON response (standard for agents)
        return r.json()
    
def create_tool(spec: dict) -> Tool:
    """
    Create a Tool object (with Action objects) from a tool spec dict.
    """
    # Build actions dict
    actions = {}
    for action_name, action_data in spec.get("actions", {}).items():
        actions[action_name] = Action(
            name=action_name,
            method=action_data.get("method", "GET"),
            path=action_data.get("path", ""),
            params=action_data.get("params", {})
        )
    
    # Create the Tool object
    tool = Tool(
        name=f"local.{spec['name']}",
        type=spec.get("type" or "remote"),
        description=spec.get("description", ""),
        vendor=spec.get("vendor", ""),
        endpoint=spec.get("endpoint", ""),
        actions=actions,
        version=spec.get("version", "0.0.0"),
        module=spec.get("module", ""),
        function=spec.get("function", ""),
        params=spec.get("params", "")
    )
    
    return tool