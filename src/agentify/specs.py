from agentify import Agent
from pathlib import Path
import yaml
import os

# Console
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()
   
def load_agent_specs(agent_dir: Path | str = "agents") -> list[dict]:
    agent_dir = Path(agent_dir)
    specs = []
    for path in agent_dir.glob("*.yaml"):
        with open(path, "r") as f:
            spec = yaml.safe_load(f)
            spec["_file"] = path.name  # optional metadata
            specs.append(spec)
    return specs


def create_agents(specs: list) -> dict[str, Agent]:
    agents = {}
    for spec in specs:
        agent = create_agent(spec)
        agents[agent.name] = agent
    return agents

def create_agent(spec: dict) -> Agent:
    name = spec.get("name")
    description = spec.get("description")
    version = spec.get("version")
    role = spec.get("role")
    model_spec = spec.get("model", {})
    model_id = model_spec.get("id")
    provider = model_spec.get("provider")
    api_key_env = model_spec.get("api_key_env")

    if api_key_env:
        api_key = os.getenv(api_key_env)
    # if not api_key:
    #     raise EnvironmentError(
    #         f"Environment variables '{api_key_env}' is not set"
    #     )
    
    agent = Agent(name=name, provider=provider, model_id=model_id, role=role, description=description, version=version)

    return agent


def show_agent_menu(agents: dict) -> "Agent":
    # console = Console()

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

