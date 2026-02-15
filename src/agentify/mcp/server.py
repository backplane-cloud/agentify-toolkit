from typing import Any, Callable, Dict, List
from fastapi import FastAPI, Request
import uvicorn
import inspect
import os
import yaml
import requests

app = FastAPI()

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


# Helpers to build inputSchema

def python_type_to_json_type(py_type):
    mapping = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
        dict: "object",
        list: "array"
    }
    return mapping.get(py_type, "string")

def build_schema_from_function(func, name, description):
    sig = inspect.signature(func)

    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        annotation = param.annotation
        json_type = python_type_to_json_type(annotation)

        properties[param_name] = {"type": json_type}

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "name": name,
        "description": description or "",
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }


# Local Tools (Functions)

def echo(args: Dict[str, Any]) -> Any:
    return args

def add(args: Dict[str, Any]) -> Any:
    return args.get("a", 0) + args.get("b", 0)

def greet(args: Dict[str, Any]) -> Any:
    return f"Hello, {args.get("name")}!"

# Register Tools

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
            "type": "str",
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        },
        handler=greet,
    )
)

# MCP Server

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})

    if not isinstance(params, dict):
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1),
            "error": {"code": -32602, "message": "Params must be an object"}
        }

    response_id = body.get("id", 1)

    # initialize
    if method == "initialize":
        result = {
            "protocolVersion": "2.0",
            "serverInfo": {
                "name": "agentify-mcp2",
                "version": "0.1.0"
            },
            "capabilities": {
                "tools": {
                    "list": True,
                    "schema": True,
                    "call": True
                }
            }
        }
        return {"jsonrpc": "2.0", "id": response_id, "result": result}


    # tools/list
    if method == "tools/list":
        tools_list = []
        for tool in _TOOL_REGISTRY.values():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })

        return {
            "jsonrpc": "2.0",
            "id": response_id,
            "result": {"tools": tools_list}
        }

    # tools/call
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in _TOOL_REGISTRY:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32601, "message": "Tool not found"}
            }
        
        tool = _TOOL_REGISTRY[tool_name]

        try:
            result = tool.handler(arguments)
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32000, "message": str(e)}
            }
    
    if method == "tools/register":
        path = params.get("path")

        if not path:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32602, "message": "Missing 'path' parameter"}
            }

        try:
            yaml_specs = load_yaml_tools(path)
            registered = []

            for tool_spec in yaml_specs:
                tool = build_tool_from_yaml(tool_spec)
                register_tool(tool)
                registered.append(tool.name)

            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "result": {"registered": registered}
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32000, "message": str(e)}
            }
        
    # Remove Tool from internal registry
    if method == "tools/deregister":
        tool_name = params.get("name")

        if not tool_name:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32602, "message": "Missing 'name' parameter"}
            }

        if tool_name not in _TOOL_REGISTRY:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            }

        try:
            del _TOOL_REGISTRY[tool_name]
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "result": {"status": "ok", "deregistered": tool_name}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32000, "message": str(e)}
            }



# YAML Loader Utility - read in tool.yaml and /path/to/tools/*.yaml
def load_yaml_tools(path: str) -> List[dict]:
    tools = []
    
    if os.path.isfile(path):
        with open(path, "r") as f:
            tools.append(yaml.safe_load(f))

    elif os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".yaml") or file.endswith(".yml"):
                full_path = os.path.join(path, file)
                with open(full_path, "r") as f:
                    tools.append(yaml.safe_load(f))
    else:
        raise ValueError(f"Invalid path: {path}")

    return tools

# Tool Factory

def build_tool_from_yaml(tool_spec: dict) -> Tool:
    name = tool_spec["name"]
    description = tool_spec.get("description", "")
    endpoint = tool_spec.get("endpoint")
    actions = tool_spec.get("actions", {})

    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "params": {"type": "object"}
        },
        "required": ["action"]
    }

    def handler(args: dict):
        import requests

        action = args.get("action")
        params = args.get("params", {})

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        action_def = actions[action]
        method = action_def.get("method", "GET").upper()
        path = action_def.get("path", "/")

        url = endpoint.rstrip("/") + path

        try:
            if method == "GET":
                resp = requests.get(url, params=params)
            elif method == "POST":
                resp = requests.post(url, json=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            resp.raise_for_status()
            return resp.json()

        except Exception as e:
            raise RuntimeError(f"API call failed: {e}")

    return Tool(
        name=f"mcp.{name}",
        description=description,
        input_schema=input_schema,
        handler=handler
    )


def start_mcp2_server(host: str = "127.0.0.1", port: int = 3333):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_mcp2_server()