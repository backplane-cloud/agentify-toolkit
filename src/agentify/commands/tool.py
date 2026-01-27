import click
from pathlib import Path

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
        raise click.BadParameter(f"Tool file '{p}' not found in: {', '.join(str(sp) for sp in search_paths)}")

    with open(resolved, "r") as f:
        spec = yaml.safe_load(f)

    click.echo(f"Name       : {spec.get('name', 'Unnamed')}")
    click.echo(f"Version    : {spec.get('version', 'N/A')}")
    click.echo(f"Description: {spec.get('description', '')}")
    click.echo(f"Vendor     : {spec.get('vendor', 'N/A')}")
    click.echo(f"Endpoint   : {spec.get('endpoint', '')}")
    click.echo("Actions:")
    for name, action in spec.get("actions", {}).items():
        method = action.get("method", "N/A")
        path = action.get("path", "")
        click.secho(f"  --> {name} [{method} {path}]", fg="red")
