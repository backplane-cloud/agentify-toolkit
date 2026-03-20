from typing import Dict
from agentify.sdk.tool import Tool

_TOOL_REGISTRY: Dict[str, Tool] = {}

def register_tool(tool: Tool) -> None:
    if tool.name in _TOOL_REGISTRY:
        raise ValueError(f"Tool already registered: {tool.name}")
    _TOOL_REGISTRY[tool.name] = tool

def deregister_tool(name: str) -> None:
    if name not in _TOOL_REGISTRY:
        raise KeyError(f"Tool '{name}' not found")
    del _TOOL_REGISTRY[name]

def get_tool(name: str) -> Tool | None:
    return _TOOL_REGISTRY.get(name)

def list_tools() -> list[Tool]:
    return list(_TOOL_REGISTRY.values())