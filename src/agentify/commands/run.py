import click
from pathlib import Path

@click.command("run")
@click.argument("path", required=False)
@click.option("--model", type=str, help="Override the model ID at runtime")
@click.option("--provider", type=str, help="Override the LLM provider at runtime")
@click.option("--server", type=str, help="Optional: run on a remote server instead of local")
def run_command(path, model, provider, server):
    """Run an agent from a YAML file or directory."""
    import yaml
    from ..agents import create_agent, create_agents
    from ..specs import load_agent_specs, load_tool_spec
    from ..tools import create_tool
    from ..cli_ui import show_agent_menu
    # from ..runtime_client import upload_agent  # Optional

    agent_path = path or "./agents"
    path = Path(agent_path)
    click.echo(f"Loading agents from: {path}")

    if server:
        if not path.is_file():
            raise click.BadParameter("Remote run only supports a single YAML file")
        # resp = upload_agent(server, str(path))
        click.echo(f"Would upload agent to server {server}")
        return

    if path.is_file():
        with open(path, "r") as f:
            spec = yaml.safe_load(f)

        agent = create_agent(spec, provider=provider, model=model)

        for tool_name in getattr(agent, "tool_names", []) or []:
            tool_path = f"examples/agents/tools/{tool_name}.yaml"
            tool_spec = load_tool_spec(tool_path)
            tool = create_tool(tool_spec)
            agent.tools[tool.name] = tool

        agent.chat()

    elif path.is_dir():
        specs = load_agent_specs(path)
        agents = create_agents(specs)
        agent = show_agent_menu(agents)
        agent.chat()
    else:
        raise click.BadParameter(f"Path does not exist: {path}")
