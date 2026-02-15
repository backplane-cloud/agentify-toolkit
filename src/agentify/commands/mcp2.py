# agentify/commands/mcp.py

import click
import requests
import json

# Agentify
from agentify.mcp.server import start_mcp2_server
from agentify.mcp.client import MCPClientHTTP

# Text UI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3333
DEFAULT_ENDPOINT = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/mcp"

console = Console()

@click.group()
def mcp2_group():
    """Manage MCP-compatible servers"""
    pass

@mcp2_group.command("start")
@click.option("--host", default="127.0.0.1", help="Host to bind MCP server")
@click.option("--port", default=3333, help="Port to bind MCP server")
def start(host: str, port: int):
    """Start MCP Server"""
    click.echo(f"Starting MCP server on {host}:{port}")
    start_mcp2_server(host=host, port=port)


@mcp2_group.command("list")
@click.option("--endpoint", default=DEFAULT_ENDPOINT, help="MCP server endpoint")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def list_tools(endpoint: str, debug: bool):
    """List tools exposed by the MCP server"""
    try:
        client = MCPClientHTTP(endpoint)
        init_result = client.initialize()
        if debug:
            # print("Server initialized:", init_result)
            console.print(
                Panel(
                    f"{init_result}",
                    title="Server initialized",
                    border_style="green",
                    expand=False,
                    box=box.ROUNDED  # use a rounded border
                )
            )

        tools = client.list_tools()
      
        # Display Tools in Table
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Input Schema", style="yellow")

        if debug:
            print(tools)
            return
        for tool in tools:
            # Optional: pretty-print schema as compact JSON string
            
            schema_str = json.dumps(tool["inputSchema"], indent=None)
            table.add_row(tool["name"], tool["description"], schema_str)

        console.print(table)

    except ConnectionError:
        print("⚠️  Could not connect to MCP server.")
        print("Please start the server by running: agentify mcp start")

    except Exception as e:
        # print(f"An error occurred while communicating with the MCP server: {e}")
        print("⚠️  Could not connect to MCP server.")
        print(f"Please start the server by running: agentify mcp start{e}")


@mcp2_group.command("invoke")
@click.argument("tool_name")
@click.option("--args",default="{}",help="JSON string of arguments to pass to the tool")
@click.option("--endpoint", default=DEFAULT_ENDPOINT, help="MCP server endpoint")
@click.option("--debug", is_flag=True, help="Enable debug mode")
def invoke_tool(tool_name: str, args: str, endpoint: str, debug: bool = False):
    """Invoke a published tool"""
    try:
        client = MCPClientHTTP(endpoint)
        client.initialize()
        arguments = json.loads(args)
        response = client.call_tool(tool_name, arguments)
        result = response.get("result", {})
        structured = result.get("structuredContent", {})
        tool_result = structured.get("result", None)

        if debug: 
            console.print(f"Call {tool_name} tool: {tool_result}")
            return
        
        result_json = json.dumps(tool_result, indent=2)
        console.print(result_json)

            
        
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON for --args:[/red] {e}")
        raise SystemExit(1)
    

@mcp2_group.command("schema")
@click.argument("tool_name")
@click.option("--endpoint", default=DEFAULT_ENDPOINT, help="MCP server endpoint")
def show_schema(tool_name: str, endpoint: str):
    """
    Show the schema of a registered tool.
    """
    try:
        client = MCPClientHTTP(endpoint)
        client.initialize()
        tools = client.list_tools()
        tool_schema = next(t for t in tools if t["name"] == tool_name)["inputSchema"]
        console.print(json.dumps(tool_schema, indent=2))

    except Exception as e:
        print(f"Error fetching schema for {tool_name}: {e}")