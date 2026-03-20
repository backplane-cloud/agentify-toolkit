import click
from pathlib import Path

@click.command("run")
@click.argument("path", required=False)
@click.option("--model", type=str, help="Override the model ID at runtime")
@click.option("--provider", type=str, help="Override the LLM provider at runtime")
@click.option("--server", type=str, help="Optional: run on a remote server instead of local")
@click.option("--debug", is_flag=True, help="Turn on debugging to see raw prompt")
@click.option("--toolprompt", is_flag=True, help="Agent prompts for approval before tool invocation")
@click.option("--showstats", is_flag=True, help="Display Token usage, cost and latency")
@click.option("--stream", is_flag=True, help="Stream response")
def run_command(path, model, provider, server, debug, toolprompt, showstats, stream):
    """Execute an agent from a YAML file or directory"""
    import yaml
    import sys
    from agentify.sdk.agent import create_agent, create_agents
    from agentify.sdk.specs import load_agent_specs

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
        agent.chat(debug=debug, toolprompt=toolprompt, showstats=showstats, stream=stream)

    elif path.is_dir():
        specs = load_agent_specs(path)
        agents = create_agents(specs)
        agent = show_agent_menu(agents)
        agent.chat()
    else:
        raise click.BadParameter(f"Path does not exist: {path}")

from rich.console import Console
from rich.table import Table

def show_agent_menu(agents: dict) -> "Agent":
    console = Console()

    table = Table(title="Available Agents", header_style="bold cyan")
    table.add_column("#", style="yellow", justify="right")
    table.add_column("AgentName", style="green")
    table.add_column("Agent Version", style="dim")
    table.add_column("Agent Role", style="dim")
    table.add_column("AI Provider", style="dim")
    table.add_column("LLM Model", style="dim")

    agent_list = list(agents.values())

    for i, agent in enumerate(agent_list, start=1):


        table.add_row(
            str(i),
            agent.name,
            agent.version,
            agent.description,
            agent.provider,
            agent.model_id,
        )

    console.print(table)

    while True:
        choice = input("Select an agent: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(agent_list):
            selected_agent = agent_list[int(choice) - 1]
            return selected_agent
        elif int(choice) == (len(agent_list) + 1):
            console.print("Create custom Agent")
        console.print("[red]Invalid selection[/red]")