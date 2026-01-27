import click
from pathlib import Path


@click.command("deploy")
@click.argument("paths", type=str)
@click.option(
    "--server",
    default="http://127.0.0.1:8001",
    help="Runtime server URL"
)
def deploy_command(paths, server):
    """
    Deploy agent YAML files to Agent Runtime server.

    Examples:
      agentify deploy agent.yaml
      agentify deploy examples/agents/
      agentify deploy examples/agents/agent1.yaml,agent2.yaml
    """
    import yaml
    import requests
    # Split comma separated inputs
    raw_paths = [p.strip() for p in paths.split(",") if p.strip()]
    if not raw_paths:
        click.echo("Please provide at least one file or folder path.")
        return

    yaml_files = []

    # Expand paths
    for path_str in raw_paths:
        p = Path(path_str)
        if p.is_file() and p.suffix.lower() in (".yaml", ".yml"):
            yaml_files.append(p)

        elif p.is_dir():
            yaml_files.extend(list(p.glob("*.yaml")) + list(p.glob("*.yml")))

        else:
            click.echo(f"Skipping invalid path: {p}")

    if not yaml_files:
        click.echo("No YAML agent files found.")
        return

    # Load YAML -> JSON specs
    agent_specs = []
    for file in yaml_files:
        try:
            with open(file, "r") as f:
                agent_specs.append(yaml.safe_load(f))
        except Exception as e:
            click.echo(f"Failed to load {file}: {e}")

    if not agent_specs:
        click.echo("No valid agent specs found.")
        return

    # Send to runtime server
    try:
        resp = requests.post(f"{server}/agents/add", json={"agents": agent_specs})
        resp.raise_for_status()
    except Exception as e:
        click.echo(f"Failed to contact runtime server at {server}: {e}")
        return

    loaded = resp.json().get("loaded", [])
    click.echo(f"✓ Deployed {len(loaded)} agent(s): {', '.join(loaded)}")
