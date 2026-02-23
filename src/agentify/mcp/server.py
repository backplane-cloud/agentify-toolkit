from fastapi import FastAPI, Request
import uvicorn
import os

from .registry import list_tools, get_tool, register_tool, deregister_tool
from .builtin_tools import register_builtin_tools 
from agentify.tool import Tool

app = FastAPI()

register_builtin_tools()

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})
    response_id = body.get("id", 1)

    if method == "initialize":
        return {"jsonrpc":"2.0","id":response_id,"result":{
            "protocolVersion":"2.0",
            "serverInfo":{"name":"agentify-mcp2","version":"0.1.0"},
            "capabilities":{"tools":{"list":True,"call":True}}
        }}

    if method == "tools/list":
        tools_list = []
        for tool in list_tools():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.to_mcp_input_schema()
            })
        return {"jsonrpc":"2.0","id":response_id,"result":{"tools":tools_list}}


    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        tool = get_tool(tool_name)

        if not tool:
            return {
                "jsonrpc":"2.0",
                "id":response_id,
                "error":{"code":-32601,"message":"Tool not found"}
            }

        try:
            if tool.type == "internal":
                result = tool.invoke(args=arguments)
            else:
                action = arguments.get("action")
                args = arguments.get("args", {})
                result = tool.invoke(action_name=action, args=args)

            return {"jsonrpc":"2.0","id":response_id,"result":result}

        except Exception as e:
            return {
                "jsonrpc":"2.0",
                "id":response_id,
                "error":{"code":-32000,"message":str(e)}
            }


    if method == "tools/register":
        path = params.get("path")
        if not path:
            return {"jsonrpc":"2.0","id":response_id,"error":{"code":-32602,"message":"Missing 'path' parameter"}}

        registered = []
        from ..tool import create_tool
        from ..specs import load_tool_specs, load_tool_spec 
        if os.path.isfile(path):
            # It's a single YAML file
            yaml_specs = [load_tool_spec(path)]
        elif os.path.isdir(path):
            # It's a directory containing multiple YAML files
            yaml_specs = load_tool_specs(path)
        else:
            raise ValueError(f"Path {path} does not exist or is not a file/directory.")


        from pathlib import Path

        for tool_spec in yaml_specs:
            yaml_file = tool_spec.get("_file")
            source_path = Path(path) / yaml_file if yaml_file else None

            base_tool = create_tool(tool_spec, source_path)

            # INTERNAL TOOL → register directly
            if base_tool.type == "internal":
                base_tool.name = f"mcp.{base_tool.name}"
                register_tool(base_tool)
                registered.append(base_tool.name)
                continue

            # REMOTE TOOL → split actions
            for action_name, action in base_tool.actions.items():

                def make_action_callable(parent_tool, action_name):
                    def _callable(**kwargs):
                        return parent_tool.invoke(action_name=action_name, args=kwargs)
                    return _callable

                action_tool = Tool(
                    name=f"mcp.{base_tool.name}.{action_name}",
                    description=f"{base_tool.description} ({action_name})",
                    vendor=base_tool.vendor,
                    type="internal",
                    version=base_tool.version,
                    params=action.params.get("query", {}) 
                            or action.params.get("body", {})
                            or {},
                    _callable=make_action_callable(base_tool, action_name)
                )

                register_tool(action_tool)
                registered.append(action_tool.name)

        return {"jsonrpc":"2.0","id":response_id,"result":{"registered":registered}}
    

    if method == "tools/deregister":
        tool_name = params.get("name")
        
        if not tool_name:
            return {"jsonrpc": "2.0","id": response_id,
                    "error": {"code": -32602, "message": "Missing 'name' parameter"}}
        
        try:
            deregister_tool(tool_name)
            return {"jsonrpc":"2.0","id": response_id,
                    "result": {"status": "ok", "deregistered": tool_name}}
        except KeyError:
            return {"jsonrpc":"2.0","id": response_id,
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
        except Exception as e:
            return {"jsonrpc":"2.0","id": response_id,
                    "error": {"code": -32000, "message": str(e)}}


def start_mcp_server(host: str="127.0.0.1", port: int=3333):
    uvicorn.run(app, host=host, port=port)

if __name__=="__main__":
    start_mcp_server()