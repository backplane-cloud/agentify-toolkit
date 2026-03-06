import click
from pathlib import Path

@click.group("agent")
def agent_group():
    """Manage agent YAML definitions (create, list, show)"""
    pass


@agent_group.command("new")
@click.argument("folder", required=False)
def create_agent_cli(folder):
    """Interactively create a new agent YAML file"""
    import yaml

    click.echo("Creating a new agent YAML...\n")
    name = click.prompt("Agent Name")
    description = click.prompt("Description", default="")
    version = click.prompt("Version", default="0.1.0")
    provider = click.prompt("Provider (e.g., openai, anthropic, xai, google, bedrock)")
    model_id = click.prompt("Model ID")
    api_key_env = click.prompt("API key environment variable name", default=f"{provider.upper()}_API_KEY")

    click.echo("Define the agent's role. Enter multiple lines, then Ctrl+D (Linux/macOS) or Ctrl+Z (Windows)")
    role_lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        role_lines.append(line)
    role = "\n".join(role_lines).strip()

    agent_spec = {
        "name": name,
        "description": description,
        "version": version,
        "model": {
            "provider": provider,
            "id": model_id,
            "api_key_env": api_key_env
        },
        "role": role
    }

    folder_path = Path(folder or ".")
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / f"{name}.yaml"

    with open(file_path, "w") as f:
        yaml.dump(agent_spec, f, sort_keys=False)

    click.echo(f"\nAgent YAML saved to {file_path}")

agent_group.add_command(create_agent_cli, name="create")
create_alias = click.Command(
    name="create",
    callback=create_agent_cli,
    hidden=True,
    help=create_agent_cli.help,
)
agent_group.add_command(create_alias)



@agent_group.command("show")
@click.argument("agent_name_or_file", required=True)
def show_agent(agent_name_or_file):
    """Show details of a single agent"""
    import yaml
    from rich.console import Console
    from rich.syntax import Syntax
    console = Console(force_terminal=True, color_system="truecolor")

    # Resolve file
    p = Path(agent_name_or_file)
    if p.suffix == "":
        p = p.with_suffix(".yaml")

    search_paths = [Path("."), Path("./agents"), Path("./examples/agents")]
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


@agent_group.command("list")
@click.argument("path", required=False, default=".")
def list_agents(path):
    """List all agent YAML files in a directory"""
    from rich.console import Console
    from rich.table import Table
    from rich.theme import Theme
    from agentify.sdk.specs import load_agent_specs

    console = Console(theme=Theme({"header": "bold cyan", "highlight": "magenta"}))

    p = Path(path)
    if not p.is_dir():
        raise click.BadParameter(f"{path} is not a directory")

    specs = load_agent_specs(p)
    if not specs:
        console.print("No agent YAML files found.", style="yellow")
        return

    # Table without borders
    table = Table(show_lines=False, show_header=True, header_style="header", box=None)
    table.add_column("Name", style="white", no_wrap=True)
    table.add_column("Provider", style="magenta")
    table.add_column("Model", style="green")
    table.add_column("Description", style="white")

    for s in specs:
        name = s.get("name", "Unnamed")
        desc = s.get("description", "")
        model_info = s.get("model", {})
        provider = model_info.get("provider", "N/A")
        model = model_info.get("id", "N/A")
        table.add_row(name, provider, model, desc)

    console.print(table)
    console.print("Use: [yellow]agentify agent show <agent_name>[/yellow] for metadata")