# agentify/commands/mcp.py

import click
import requests
from agentify.mcpserver.server import start_mcp_server
from rich.console import Console
from rich.table import Table
import json
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


@click.group()
def mcp_group():
    """Manage MCP servers"""
    pass


@mcp_group.command("start")
@click.option("--host", default="127.0.0.1", help="Host to bind MCP server")
@click.option("--port", default=3333, help="Port to bind MCP server")
def start(host: str, port: int):
    """Start the MCP server"""
    click.echo(f"Starting MCP server on {host}:{port}")
    start_mcp_server(host=host, port=port)

@mcp_group.command("list")
@click.option("--endpoint", default="http://127.0.0.1:3333", help="MCP server endpoint")
def list_tools(endpoint: str):
    """List tools exposed by the MCP server"""

    url = f"{endpoint}/tools"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        console.print(f"[red]Error connecting to MCP server:[/red] {e}")
        raise SystemExit(1)

    data = response.json()
    tools = data.get("tools", [])

    if not tools:
        console.print("[yellow]No tools found.[/yellow]")
        return

    table = Table(
        title="MCP Tools",
        show_header=True,
        header_style="bold",
        box=None,              # 👈 no borders
        pad_edge=False
    )

    table.add_column("Tool Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    for tool in tools:
        table.add_row(
            tool.get("name", ""),
            tool.get("description", "") or ""
        )

    console.print(table)

@mcp_group.command("invoke")
@click.argument("tool_name")
@click.option(
    "--args",
    default="{}",
    help="JSON string of arguments to pass to the tool",
)
@click.option(
    "--endpoint",
    default="http://127.0.0.1:3333",
    help="MCP server endpoint",
)
def invoke_tool(tool_name: str, args: str, endpoint: str):
    """Invoke a tool exposed by the MCP server"""
    try:
        arguments = json.loads(args)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON for --args:[/red] {e}")
        raise SystemExit(1)

    url = f"{endpoint}/tools/{tool_name}/invoke"

    try:
        response = requests.post(
            url,
            json={"arguments": arguments},
            timeout=10,
        )
        response.raise_for_status()
    except requests.HTTPError:
        console.print(
            f"[red]Tool invocation failed:[/red] {response.text}"
        )
        raise SystemExit(1)
    except requests.RequestException as e:
        console.print(f"[red]Error connecting to MCP server:[/red] {e}")
        raise SystemExit(1)

    data = response.json()
    result = data.get("result")

    # Pretty output
    if isinstance(result, (dict, list)):
        pretty = json.dumps(result, indent=2)
        syntax = Syntax(pretty, "json", theme="ansi_dark", line_numbers=False)
        console.print(Panel(syntax, title="Result"))
    else:
        console.print(Panel(str(result), title="Result"))
