"""
Copyright 2026 Backplane Software
Licensed under the Apache License, Version 2.0
Author: Lewis Sheridan
Description: Agentify class to build multi-model AI Agents
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Any
import requests
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

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
    version: Optional[str] = field(default="0.0.0")
    
    # API Tool
    endpoint: Optional[str] = None # for remote    
    actions: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)

    # Function Tooll Note: When type == internal, then it's a function e.g. (tool.yaml + tool.py)
    _callable: Optional[Callable[..., Any]] = field(default=None, repr=False)


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

    def to_mcp_input_schema(self) -> dict:
        if self.type == "internal":
            return {
                "type": "object",
                "properties": self.params or {},
                "required": list(self.params.keys())
            }

        if self.type == "remote":
            # For now, simplest model:
            # Flatten all action params into a single object
            return {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "args": {
                        "type": "object",
                        "properties": {},
                    }
                },
                "required": ["action"]
            }

        raise RuntimeError(f"Unsupported tool type '{self.type}'")

    
    def invoke(self, action_name: Optional[str] = None, args: dict = None):
        args = args or {}

        # Function Tool
        if self._callable:
            return self._callable(**args)
            
        # API Tool
        if self.actions:
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

            if r.status_code >= 400:
                return {
                    "error": True,
                    "status": r.status_code,
                    "response": r.text
                }

            return r.json()
        
        raise RuntimeError("Tool not executable")

    # New helper: create an MCP-registered tool dict
    def to_mcp_tool_dict(self) -> dict:
        return {
            "name": self.name.replace("local.", "mcp."),  # optional namespace adjustment
            "description": self.description,
            "inputSchema": self.to_mcp_input_schema(),
            "handler": self._callable
        }

def create_tool(spec: dict, source_path: Optional[Path] = None) -> Tool:
    """
    Create a Tool object from a YAML spec dict.

    - For internal tools: dynamically load the Python function from <tool_name>.py
      in the same folder as the YAML file.
    - For API tools: create Action objects.
    
    Args:
        spec: Loaded YAML dict for the tool
        source_path: Path to the YAML file (used to locate the corresponding .py)
    """
  
    actions = {}
    callable_fn = None

    # ----------------------------
    # Internal (function-based) tool
    # ----------------------------
    if spec.get("type") == "internal":
        if not source_path:
            raise RuntimeError(f"source_path required to load internal tool '{spec.get('name')}'")

        function_name = spec.get("function")
        if not function_name:
            raise RuntimeError(f"Internal tool '{spec.get('name')}' missing 'function' field")

        # Python file is <tool_name>.py in the same folder as the YAML
        py_file = source_path.parent / f"{source_path.stem}.py"
        if not py_file.exists():
            raise FileNotFoundError(f"Python file not found for internal tool '{spec.get('name')}' at {py_file}")

        
        # Dynamically load module
        module_spec = spec_from_file_location(f"{source_path.stem}_module", py_file)
        module = module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

    

        # Get the callable function
        try:
            callable_fn = getattr(module, function_name)
        except AttributeError:
            raise RuntimeError(f"Function '{function_name}' not found in {py_file}")

    # ----------------------------
    # API-based tool
    # ----------------------------
    else:
        for action_name, action_data in spec.get("actions", {}).items():
            actions[action_name] = Action(
                name=action_name,
                method=action_data.get("method", "GET"),
                path=action_data.get("path", ""),
                params=action_data.get("params", {})
            )

    # ----------------------------
    # Create Tool object
    # ----------------------------
    tool = Tool(
        name=spec["name"],
        type=spec.get("type", "remote"),
        description=spec.get("description", ""),
        vendor=spec.get("vendor", ""),
        endpoint=spec.get("endpoint", ""),
        actions=actions,
        version=spec.get("version", "0.0.0"),
        _callable=callable_fn,
        params=spec.get("params", {})
    )
    return tool