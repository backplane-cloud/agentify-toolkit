"""
Copyright 2026 Backplane Software
Licensed under the Apache License, Version 2.0
Author: Lewis Sheridan
Description: Agentify class to build multi-model AI Agents
"""

from dataclasses import dataclass, field
from typing import Optional

from agentify.providers import run_openai, run_anthropic, run_google, run_bedrock, run_x
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


@dataclass
class Agent:
    name: str
    description: str
    provider: str
    model_id: str
    role: str
    version: Optional[str] = field(default="0.0.0")


    def get_model(self) -> str:
        return self.model_id
    
    def run(self, user_prompt: str) -> str:
        match self.provider.lower():
            case "openai":
                return run_openai(self.model_id, user_prompt)
            case "anthropic":
                return run_anthropic(self.model_id, user_prompt)
            case "google":
                return run_google(self.model_id, user_prompt)
            case "bedrock":
                return run_bedrock(self.model_id, user_prompt)
            case "x":
                return run_x(self.model_id, user_prompt)
            case _:
                raise ValueError(f"Unsupported provider: {self.provider}")

    def chat(agent: Agent):
        console = Console()
        menu_text = f"Hi I am {agent.name} and I am configured with the role of {agent.role}. I will be using the {agent.model_id} LLM for our interactions. "
        robot = ">_b"
        console.print(Panel(
            f"[bold cyan][/bold cyan]\n[bold cyan]{robot} [/bold cyan]\n{menu_text}\n[dim]Developed by Backplane Software 2026 - v0.1.0[/dim]",
            border_style="cyan"
        ))
        while True:
            prompt = Prompt.ask("\nEnter your prompt ('/exit' to quit)").strip()
            if prompt.lower() in ["/exit", "quit"]:
                console.print("[yellow]Exiting. Goodbye![/yellow]")
                break
                

            full_prompt = f"You must assume the role of {agent.role} when responding to this prompt:\n\n{prompt}"
            with console.status(f"[blue]Sending prompt to model... {agent.name} is thinking...[/blue]", spinner="dots"):
                # response = agent.run(full_prompt)
                response = agent.run(full_prompt)
            console.print(Panel.fit(response, title="Agent Response", border_style="green"))
