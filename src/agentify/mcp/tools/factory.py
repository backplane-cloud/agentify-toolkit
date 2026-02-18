from .registry import Tool, register_tool
from typing import Dict, Any, Callable
import inspect
from pathlib import Path
import importlib.util
import sys
import requests

def build_handler_for_internal(func: Callable, params_yaml: Dict[str, Any]) -> Callable[[Dict[str, Any]], Any]:
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


def load_python_function_from_file(yaml_path: str, func_name: str) -> Callable:
    yaml_path = Path(yaml_path).resolve()
    py_file = yaml_path.with_suffix(".py")
    if not py_file.exists():
        raise FileNotFoundError(f"Python file not found next to YAML: {py_file}")
    module_name = py_file.stem
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    if not hasattr(module, func_name):
        raise AttributeError(f"Function '{func_name}' not found in {py_file}")
    return getattr(module, func_name)


def create_tool(yaml_path: str, tool_spec: dict, action_name: str = None) -> Tool:
    name = tool_spec["name"]
    description = tool_spec.get("description", "")
    tool_type = tool_spec.get("type", "external")

    if tool_type == "internal":
        func_name = tool_spec["function"]
        func = load_python_function_from_file(yaml_path, func_name)
        params_yaml = tool_spec.get("params", {})
        input_schema = {"type": "object", "properties": {}, "required": []}
        for param_name, param_def in params_yaml.items():
            param_type = param_def.get("type", "string")
            input_schema["properties"][param_name] = {"type": param_type}
            if param_def.get("required", False):
                input_schema["required"].append(param_name)
        handler = build_handler_for_internal(func, params_yaml)
        return Tool(name=f"mcp.{name}", description=description, input_schema=input_schema, handler=handler)

    else:  # API / external
        endpoint = tool_spec.get("endpoint")
        actions = tool_spec.get("actions", {})
        if action_name is None:
            raise ValueError(f"No action_name provided for API tool: {name}")
        action_def = actions[action_name]
        method = action_def.get("method", "GET").upper()
        path = action_def.get("path", "/")
        action_params = action_def.get("params", {})
        input_schema = {"type": "object", "properties": {}, "required": []}
        for loc, param_group in action_params.items():
            for param_name, param_type in param_group.items():
                input_schema["properties"][param_name] = {"type": param_type}
                input_schema["required"].append(param_name)

        def handler(args: dict):
            if method == "GET":
                resp = requests.get(endpoint.rstrip("/") + path, params=args)
            elif method == "POST":
                resp = requests.post(endpoint.rstrip("/") + path, json=args)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            resp.raise_for_status()
            return resp.json()

        return Tool(name=f"mcp.{name}.{action_name}", description=f"{description} - action: {action_name}", input_schema=input_schema, handler=handler)
