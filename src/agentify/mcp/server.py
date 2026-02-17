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

# Build Tool Schema from function
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

    # initialize (MCP-compliant)
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


    # tools/list (MCP-compliant)
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

    # tools/call (MCP-compliant)
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
    
    # Custom methods for dynamic tool loading
    # e.g. agentify mcp2 register tool.yaml or path/to/tool/folder
    # It loads tool.yaml or tool.yaml/python.py for function-based tools

    # tools/register
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

            for yaml_path, tool_spec in yaml_specs:
                tool = build_tool_from_yaml(yaml_path, tool_spec)
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
        
    # tools/deregister
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
def load_yaml_tools(path: str):
    tools = []
    
    if os.path.isfile(path):
        with open(path, "r") as f:
            tools.append((path, yaml.safe_load(f)))

    elif os.path.isdir(path):
        for file in os.listdir(path):
            if file.endswith(".yaml") or file.endswith(".yml"):
                full_path = os.path.join(path, file)
                with open(full_path, "r") as f:
                    tools.append((full_path, yaml.safe_load(f)))
    else:
        raise ValueError(f"Invalid path: {path}")

    return tools




from pathlib import Path
import importlib.util
import sys
from typing import Callable

def load_python_function_from_file(yaml_path: str, func_name: str) -> Callable:
    """
    Load a Python function from a .py file located next to the YAML.
    """
    yaml_path = Path(yaml_path).resolve()
    py_file = yaml_path.with_suffix(".py")  # same base name, .py extension

    if not py_file.exists():
        raise FileNotFoundError(f"Python file not found next to YAML: {py_file}")

    module_name = py_file.stem  # e.g., add_numbers
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore

    if not hasattr(module, func_name):
        raise AttributeError(f"Function '{func_name}' not found in {py_file}")

    return getattr(module, func_name)


# Build hanlder for internal
import inspect
from typing import Dict, Any

def build_handler_for_internal(func: Callable, params_yaml: Dict[str, Any]) -> Callable[[Dict[str, Any]], Any]:
    """
    Wrap a Python function as an MCP tool handler.

    Args:
        func: Python function to wrap
        params_yaml: dict describing expected params from YAML

    Returns:
        handler: callable taking args dict
    """
    sig = inspect.signature(func)
    
    def handler(args: Dict[str, Any]) -> Any:
        func_args = {}
        for param in sig.parameters.values():
            name = param.name
            if name in args:
                func_args[name] = args[name]
            elif param.default != inspect.Parameter.empty:
                func_args[name] = param.default
            else:
                raise ValueError(f"Missing required argument: {name}")
        return func(**func_args)

    return handler


# Tool Factory

def build_tool_from_yaml(yaml_path: str, tool_spec: dict) -> Tool:
    """
    Build a Tool object from YAML spec.

    Handles both internal (Python) and external (API) tools.
    """
    name = tool_spec["name"]
    description = tool_spec.get("description", "")
    tool_type = tool_spec.get("type", "external")
    
    if tool_type == "internal":
        # Load Python function
        func_name = tool_spec["function"]
        func = load_python_function_from_file(yaml_path, func_name)

        # Build input_schema from 'params'
        params_yaml = tool_spec.get("params", {})
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }

        for param_name, param_def in params_yaml.items():
            param_type = param_def.get("type", "string")
            input_schema["properties"][param_name] = {"type": param_type}
            if param_def.get("required", False):
                input_schema["required"].append(param_name)

        handler = build_handler_for_internal(func, params_yaml)

        return Tool(
            name=f"mcp.{name}",
            description=description,
            input_schema=input_schema,
            handler=handler
        )

    else:  # API / external tool
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