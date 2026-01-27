import click
from pathlib import Path

@click.group("agent")
def agent_group():
    """Create, List and Show agent YAML files"""
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

@agent_group.command("list")
@click.argument("path", required=False, default=".")
def list_agents(path):
    """List all agent YAML files in a directory"""
    from ..specs import load_agent_specs

    p = Path(path)
    if not p.is_dir():
        raise click.BadParameter(f"{path} is not a directory")

    specs = load_agent_specs(p)
    if not specs:
        click.echo("No agent YAML files found.")
        return

    click.echo(f"Found {len(specs)} agent(s) in {path}:")
    click.secho(f"{'NAME':20} {'PROVIDER':20} {'MODEL':20} {'DESCRIPTION'}", fg="cyan")
    click.echo("-" * 80)
    for s in specs:
        name = s.get("name", "Unnamed")
        desc = s.get("description", "")
        provider = s.get("model","").get("provider")
        model = s.get("model","").get("id")
        click.echo(f"{name:<20} {provider:<20} {model:<20} {desc}")

    click.secho("\nUse: agentify agent show <agent_name> for metadata", fg="yellow")


@agent_group.command("show")
@click.argument("agent_name_or_file", required=True)
def show_agent(agent_name_or_file):
    """Show details of a single agent"""
    import yaml

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
        raise click.BadParameter(f"Agent file '{p}' not found in: {', '.join(str(sp) for sp in search_paths)}")

    with open(resolved, "r") as f:
        spec = yaml.safe_load(f)

    click.echo(f"Name       : {spec.get('name', 'Unnamed')}")
    click.echo(f"Description: {spec.get('description', '')}")
    click.echo(f"Version    : {spec.get('version', 'N/A')}")
    click.echo(f"Role       : {spec.get('role', '').strip()}")
    model = spec.get("model", {})
    click.echo(f"Model      : {model.get('id', 'N/A')} ({model.get('provider', '')})")
    click.echo(f"Tools      : {spec.get('tools', '')}")
