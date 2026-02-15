from fastapi import FastAPI, Request
import uvicorn
import inspect

from mcp_serializer.registry import MCPRegistry
from mcp_serializer.initializer import MCPInitializer
from mcp_serializer.serializers import MCPSerializer

registry = MCPRegistry()
initializer = MCPInitializer()
serializer = MCPSerializer(initializer=initializer, registry=registry)

app = FastAPI()

# -----------------------------
# MCP Tool Metadata Store
# -----------------------------

TOOL_SCHEMAS = {}


# -----------------------------
# Helpers
# -----------------------------

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
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }


def register_tool(name: str, description: str):
    """
    Decorator that:
    1. Registers tool with MCPRegistry
    2. Builds and stores JSON schema for MCP introspection
    """
    def decorator(func):
        registry.tool(name=name, description=description)(func)

        TOOL_SCHEMAS[name] = build_schema_from_function(
            func=func,
            name=name,
            description=description
        )

        return func

    return decorator


# -----------------------------
# Tool Registration
# -----------------------------

@register_tool("add", "Add two numbers together")
def add(a: int, b: int) -> dict:
    return {"result": a + b}


@register_tool("greet", "Return a greeting for a user")
def greet(name: str) -> dict:
    return {"result": f"Hello, {name}!"}

@register_tool(
    name="random_user",
    description="Generate random user data"
)
def random_user(page: int = 1, limit: int = 1) -> dict:
    """
    Calls the RandomUser API and returns user data.

    Args:
        page (int): page number to fetch, default 1
        limit (int): number of results to return, default 1

    Returns:
        dict: {"result": <list of users>}
    """
    import requests

    url = "https://randomuser.me/api/"
    params = {
        "page": page,
        "results": limit
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise exception on HTTP errors

    data = response.json()
    return {"result": data.get("results", [])}



# -----------------------------
# MCP Endpoint
# -----------------------------

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

    # -------------------------
    # initialize
    # -------------------------
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

    # -------------------------
    # tools/list
    # -------------------------
    if method == "tools/list":
        tools_list = []
        for name, schema in TOOL_SCHEMAS.items():
            tools_list.append({
                "name": name,
                "description": schema.get("description", "")
            })
        return {
            "jsonrpc": "2.0",
            "id": response_id,
            "result": {"tools": tools_list}
        }

    # -------------------------
    # tools/schema
    # -------------------------
    if method == "tools/schema":
        tool_name = params.get("tool_name")
        if not tool_name:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32602, "message": "Missing 'tool_name'"}
            }

        schema = TOOL_SCHEMAS.get(tool_name)
        if not schema:
            return {
                "jsonrpc": "2.0",
                "id": response_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            }

        return {"jsonrpc": "2.0", "id": response_id, "result": schema}

    # -------------------------
    # tools/call
    # -------------------------
    if method == "tools/call":
        result = serializer.process_request(body).response_data
        return {"jsonrpc": "2.0", "id": response_id, "result": result}

    # -------------------------
    # unknown method
    # -------------------------
    return {
        "jsonrpc": "2.0",
        "id": response_id,
        "error": {"code": -32601, "message": f"Unknown method '{method}'"}
    }


def start_mcp2_server(host: str = "127.0.0.1", port: int = 3333):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_mcp2_server()
