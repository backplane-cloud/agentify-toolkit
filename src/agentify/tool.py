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
    endpoint: str
    actions: dict = field(default_factory=dict)
    version: Optional[str] = field(default="0.0.0")

    def to_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description or f"Tool {self.name}",
            "actions": [
                action.to_schema()
                for action in self.actions.values()
            ]
        }

    def invoke(self, action_name: str, args: dict):
        # find action
        action = self.actions.get(action_name)
        if not action:
            raise ValueError(f"Unknown action '{action_name}' for tool '{self.name}'")

        # build URL
        url = f"{self.endpoint}{action.path}"

        # route based on action.method
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