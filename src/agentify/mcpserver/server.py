# src/mcpserver/server.py

from typing import Any, Callable, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Agentify MCP Server",
    version="0.1.0",
    description="Minimal HTTP MCP server for tool discovery and invocation",
)

#
# ---- Tool model -----------------------------------------------------------
#

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


#
# ---- In-memory registry ---------------------------------------------------
#

_TOOL_REGISTRY: Dict[str, Tool] = {}


def register_tool(tool: Tool) -> None:
    if tool.name in _TOOL_REGISTRY:
        raise ValueError(f"Tool already registered: {tool.name}")
    _TOOL_REGISTRY[tool.name] = tool


#
# ---- API models -----------------------------------------------------------
#

class InvokeRequest(BaseModel):
    arguments: Dict[str, Any]


class InvokeResponse(BaseModel):
    result: Any


#
# ---- MCP endpoints --------------------------------------------------------
#

@app.get("/tools")
def list_tools():
    """
    List all available tools.
    """
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in _TOOL_REGISTRY.values()
        ]
    }


@app.post("/tools/{tool_name}/invoke", response_model=InvokeResponse)
def invoke_tool(tool_name: str, request: InvokeRequest):
    """
    Invoke a tool by name.
    """
    tool = _TOOL_REGISTRY.get(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    try:
        result = tool.handler(request.arguments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return InvokeResponse(result=result)


#
# ---- Example tools --------------------------------------------------------
# (These make the server self-demonstrating)
#

def echo_tool(args: Dict[str, Any]) -> Any:
    return args


def add_tool(args: Dict[str, Any]) -> Any:
    return args.get("a", 0) + args.get("b", 0)


register_tool(
    Tool(
        name="echo",
        description="Echo back the provided arguments",
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        },
        handler=echo_tool,
    )
)

register_tool(
    Tool(
        name="add",
        description="Add two numbers",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
        handler=add_tool,
    )
)


#
# ---- Entrypoint -----------------------------------------------------------
#

def start_mcp_server(host: str = "127.0.0.1", port: int = 3333):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_mcp_server()
