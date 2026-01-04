# Copyright 2026 Backplane
# Licensed under the Apache License, Version 2.0


import click
from pathlib import Path
import yaml
# from .engine import run_agentify
from .specs import create_agent, load_agent_specs, create_agents, show_agent_menu

@click.group()
def main():
    """Agentify - Declarative AI Agents"""
    pass

@main.command()
@click.argument("path", required=False)
def run(path):
    """
    run agent.yaml or run <folder> containing agent YAMLS

    PATH can be:
      - A single YAML file → runs that agent directly
      - A folder containing YAML files → presents a menu to select an agent
    """

    agent_path = path or "./agents"
    path = Path(agent_path)
    click.echo(f"Loading agents from: {path}")


    # Single-agent mode
    if path.is_file():
        
        # Load YAML File
        with open(path, "r") as f:
            spec = yaml.safe_load(f)


        # Create Agent
        agent = create_agent(spec)

        # Run Agent
        agent.chat()

    elif path.is_dir():
        # Multi-agent mode

        # Load specs from ./agent/*.yaml
        specs = load_agent_specs(path)  

        # For each Spec create an Agent
        agents = create_agents(specs) 

        # Show menu to select which agent to run. 
        agent = show_agent_menu(agents) 

        # Run selected agent.
        # run_agent(selected_agent) 
        agent.chat()

    else:
        raise click.BadParameter(f"Path does not exist: {path}")

@main.command()
@click.argument("path", required=False)
def list(path):
    """
    List agents in a folder and select one to run (interactive TUI)
    """

    agent_path = path or "./agents"
    path = Path(agent_path)
    click.echo(f"Listing agents from: {path}")

    if not path.is_dir():
        raise click.BadParameter(f"Path is not a directory: {path}")

    # Load specs from folder
    specs = load_agent_specs(path)

    if not specs:
        click.echo("No agent YAML files found.")
        return

    # Create agents
    agents = create_agents(specs)

    # Interactive menu
    agent = show_agent_menu(agents)

    # Run selected agent
    agent.chat()



if __name__ == "__main__":
    main()