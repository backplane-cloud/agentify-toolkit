import click
from pathlib import Path
import yaml
import requests

@click.group("tool")
def tool_group():
    """List and Show tool YAML files"""
    pass


@tool_group.command("list")
@click.argument("path", required=False, default=".")
def list_tools(path):
    """List all tool YAML files in a directory."""
    from ..specs import load_tool_specs

    p = Path(path)
    if not p.is_dir():
        raise click.BadParameter(f"{path} is not a directory")

    specs = load_tool_specs(p)
    if not specs:
        click.echo("No tool YAML files found.")
        return

    click.echo(f"Found {len(specs)} tool(s) in {path}:")
    click.secho(f"{'NAME':15} {'DESCRIPTION':30} {'VENDOR':20} {'ENDPOINT'}", fg="cyan")
    click.echo("-" * 80)
    for s in specs:
        name = s.get("name", "Unnamed")
        desc = s.get("description", "")
        vendor = s.get("vendor", "")
        endpoint = s.get("endpoint", "")
        click.echo(f"{name:<15} {desc:<30} {vendor:<20} {endpoint}")

    click.secho("\nUse: agentify tool show <tool_name> for metadata", fg="yellow")



@tool_group.command("show")
@click.argument("tool_name_or_file", required=True)
def show_tool(tool_name_or_file):
    """Show details of a single tool"""
    import yaml
    from rich.console import Console
    from rich.syntax import Syntax
    console = Console(force_terminal=True, color_system="truecolor")

    # Resolve file
    p = Path(tool_name_or_file)
    if p.suffix == "":
        p = p.with_suffix(".yaml")

    search_paths = [Path("."), Path("./tools"), Path("./examples/agents/tools")]
    resolved = None
    for base in search_paths:
        candidate = base / p
        if candidate.is_file():
            resolved = candidate
            break

    if not resolved:
        raise click.BadParameter(
            f"Agent file '{p}' not found in: {', '.join(str(sp) for sp in search_paths)}"
        )

    # Load YAML spec
    with open(resolved, "r") as f:
        spec = yaml.safe_load(f)


    # Pretty YAML output with syntax highlighting
    yaml_text = yaml.dump(spec, sort_keys=False, default_flow_style=False)
    syntax = Syntax(yaml_text, "yaml", theme="monokai", line_numbers=False)
    console.print(syntax)

@tool_group.command()
@click.argument(
    "tool_yaml",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--server", default="http://localhost:3333",
    required=True,
    help="MCP server URL (e.g. http://localhost:3333)",
)
def publish(tool_yaml: Path, server: str):
    """
    Publish a tool to an MCP server from a YAML definition.
    """
    # 1. Load YAML
    try:
        with tool_yaml.open("r") as f:
            tool_spec = yaml.safe_load(f)
    except Exception as e:
        raise click.ClickException(f"Failed to load YAML: {e}")

    if not isinstance(tool_spec, dict):
        raise click.ClickException("Tool YAML must define a mapping/object")

    # 2. POST to MCP server
    url = f"{server.rstrip('/')}/tools"

    try:
        response = requests.post(url, json=tool_spec, timeout=10)
    except requests.RequestException as e:
        raise click.ClickException(f"Failed to connect to MCP server: {e}")

    # 3. Handle response
    if response.status_code != 200:
        try:
            detail = response.json().get("detail")
        except Exception:
            detail = response.text
        raise click.ClickException(
            f"Failed to publish tool ({response.status_code}): {detail}"
        )

    result = response.json()
    tool_name = result.get("tool", "<unknown>")

    click.echo(f"✓ Tool published: {tool_name}")