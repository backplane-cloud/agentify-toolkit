from typing import Any, Callable, Dict

class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler


_TOOL_REGISTRY: Dict[str, Tool] = {}


def register_tool(tool: Tool) -> None:
    if tool.name in _TOOL_REGISTRY:
        raise ValueError(f"Tool already registered: {tool.name}")
    _TOOL_REGISTRY[tool.name] = tool

def deregister_tool(name: str) -> None:
    """
    Remove a tool from the registry.
    Raises KeyError if tool not found.
    """
    if name not in _TOOL_REGISTRY:
        raise KeyError(f"Tool '{name}' not found")
    del _TOOL_REGISTRY[name]

def get_tool(name: str) -> Tool:
    return _TOOL_REGISTRY.get(name)


def list_tools() -> list[Tool]:
    return list(_TOOL_REGISTRY.values())
