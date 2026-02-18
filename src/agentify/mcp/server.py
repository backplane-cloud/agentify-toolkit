from fastapi import FastAPI, Request
import uvicorn

from .tools.registry import list_tools, get_tool, register_tool, deregister_tool
from .tools.factory import create_tool
from .tools.yaml_loader import load_yaml_tools
from .tools.builtin_tools import register_builtin_tools

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
                "inputSchema": tool.input_schema
            })
        return {"jsonrpc":"2.0","id":response_id,"result":{"tools":tools_list}}

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        tool = get_tool(tool_name)
        if not tool:
            return {"jsonrpc":"2.0","id":response_id,"error":{"code":-32601,"message":"Tool not found"}}
        try:
            result = tool.handler(arguments)
            return {"jsonrpc":"2.0","id":response_id,"result":result}
        except Exception as e:
            return {"jsonrpc":"2.0","id":response_id,"error":{"code":-32000,"message":str(e)}}

    if method == "tools/register":
        path = params.get("path")
        if not path:
            return {"jsonrpc":"2.0","id":response_id,"error":{"code":-32602,"message":"Missing 'path' parameter"}}

        registered = []
        yaml_specs = load_yaml_tools(path)
        for yaml_path, tool_spec in yaml_specs:
            tool_type = tool_spec.get("type","external")
            if tool_type=="internal":
                tool = create_tool(yaml_path, tool_spec)
                register_tool(tool)
                registered.append(tool.name)
            else:
                actions = tool_spec.get("actions", {})
                if not actions:
                    tool = create_tool(yaml_path, tool_spec)
                    register_tool(tool)
                    registered.append(tool.name)
                else:
                    for action_name in actions:
                        tool = create_tool(yaml_path, tool_spec, action_name=action_name)
                        register_tool(tool)
                        registered.append(tool.name)

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