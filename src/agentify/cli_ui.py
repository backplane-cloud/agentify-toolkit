# Copyright 2026 Backplane Software
# Licensed under the Apache License, Version 2.0

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
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

