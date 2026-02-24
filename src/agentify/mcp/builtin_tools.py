from typing import Dict, Any
from .registry import register_tool
from agentify.tool import Tool

# Handlers
def add(**kwargs):
    return kwargs.get("a", 0) + kwargs.get("b", 0)

def echo(**kwargs):
    return kwargs

def greet(**kwargs):
    return f"Hello, {kwargs.get('name')}!"


# Registration function
def register_builtin_tools():
    tools = [
        Tool(
            name="mcp.echo",
            description="Echo back the provided arguments",
            vendor="agentify",
            type="internal",
            _callable=echo,
            params={},
        ),
        Tool(
            name="mcp.add",
            description="Add two numbers",
            vendor="agentify",
            type="internal",
            _callable=add,
            params={"a": {"type": "number"}, "b": {"type": "number"}},
        ),
        Tool(
            name="mcp.greet",
            description="Return a greeting for a user",
            vendor="agentify",
            type="internal",
            _callable=greet,
            params={"name": {"type": "string"}},
        ),
    ]

    for tool in tools:
        # Register in MCP shape
        register_tool(tool)
