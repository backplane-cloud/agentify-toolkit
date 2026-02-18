from typing import Dict, Any
from .registry import Tool, register_tool

# Handlers
def echo(args: Dict[str, Any]) -> Any:
    return args

def add(args: Dict[str, Any]) -> Any:
    return args.get("a", 0) + args.get("b", 0)

def greet(args: Dict[str, Any]) -> Any:
    return f"Hello, {args.get('name')}!"

# Registration function
def register_builtin_tools():
    register_tool(
        Tool(
            name="mcp.echo",
            description="Echo back the provided arguments",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": True,
            },
            handler=echo,
        )
    )

    register_tool(
        Tool(
            name="mcp.add",
            description="Add two numbers",
            input_schema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
            handler=add,
        )
    )

    register_tool(
        Tool(
            name="mcp.greet",
            description="Return a greeting for a user",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
            handler=greet,
        )
    )
