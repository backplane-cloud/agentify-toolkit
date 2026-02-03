import click
from pathlib import Path

@click.command("run")
@click.argument("path", required=False)
@click.option("--model", type=str, help="Override the model ID at runtime")
@click.option("--provider", type=str, help="Override the LLM provider at runtime")
@click.option("--server", type=str, help="Optional: run on a remote server instead of local")
@click.option("--debug", is_flag=True, help="Turn on debugging to see raw prompt")
def run_command(path, model, provider, server, debug):
    """Run an agent from a YAML file or directory."""
    import yaml
    import sys
    from ..agent import create_agent, create_agents
    from ..specs import load_agent_specs
    from ..cli_ui import show_agent_menu
    # from ..runtime_client import upload_agent  # Optional

    agent_path = path or "./agents"
    path = Path(agent_path)
    click.echo(f"Loading agents from: {path}")

    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))

    if server:
        if not path.is_file():
            raise click.BadParameter("Remote run only supports a single YAML file")
        click.echo(f"Would upload agent to server {server}")
        return

    if path.is_file():
        with open(path, "r") as f:
            spec = yaml.safe_load(f)

        agent = create_agent(spec, provider=provider, model=model, agent_file=path.resolve())
        agent.chat(debug=debug)

    elif path.is_dir():
        specs = load_agent_specs(path)
        agents = create_agents(specs)
        agent = show_agent_menu(agents)
        agent.chat()
    else:
        raise click.BadParameter(f"Path does not exist: {path}")
