"""
Copyright 2026 Backplane Software
Licensed under the Apache License, Version 2.0
Author: Lewis Sheridan
Description: Agentify class to build multi-model AI Agents
"""

from dataclasses import dataclass, field
from typing import Optional
import json

from agentify.providers import run_openai, run_anthropic, run_google, run_bedrock, run_x, run_deepseek, run_mistral, run_ollama, run_ollama_local, run_ollama_stream
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
    tool_names: list = field(default_factory=list) # From agent.yaml
    tools: dict = field(default_factory=dict) # Tool Objects


    def get_model(self) -> str:
        return self.model_id

    def get_tools(self) -> str:
        return self.tools.keys()
    
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
            case "deepseek":
                return run_deepseek(self.model_id, user_prompt)
            case "mistral":
                return run_mistral(self.model_id, user_prompt)
            case "ollama":
                return run_ollama(self.model_id, user_prompt)
            case "ollama_local":
                return run_ollama_local(self.model_id, user_prompt)
            case _:
                raise ValueError(f"Unsupported provider: {self.provider}")

    def chat(agent: "Agent"):
        console = Console()
        console.print(Panel(
            f"[bold cyan][/bold cyan]\n[bold cyan]{agent.name.upper()} [/bold cyan] [dim]{agent.version}[/dim]\nRole: {agent.description}\nUsing [yellow]{agent.model_id}[/yellow] by {agent.provider}\nTools: {agent.tool_names}",
            border_style="cyan"
        ))
        while True:
            prompt = Prompt.ask("\nEnter your prompt ('/exit' to quit)").strip()
            if prompt.lower() in ["/exit", "quit"]:
                console.print("[yellow]Exiting. Goodbye![/yellow]")
                break
                
            full_prompt = f"You must assume the role of {agent.role} when responding to this prompt:\n\n{prompt}"
            
            # Check Agent has tools
            tool_schemas = [tool.to_schema() for tool in agent.tools.values()] if agent.tools else None
            
            # If Tools available, inject them into the prompt
            if tool_schemas:
                full_prompt +='\n\nWhen you want to use a tool, reply ONLY with JSON using this format:{"tool": "<tool>", "action": "<action>", "args": {...}} Do not include extra text or explanations. If no tool is needed, reply with a natural language answer.'
                tools_block = "\n\nTOOLS:\n" + json.dumps(tool_schemas, indent=2)
                full_prompt += tools_block

            with console.status(f"[blue]Sending prompt to model... {agent.name} is thinking...[/blue]", spinner="dots"):
                response = agent.run(full_prompt)
            
            # Agentic Loop - If LLM responds with JSON for tool call.
            try: 
                data = json.loads(response) # Get JSON data
                tool_name = data.get("tool")
                action_name = data.get("action")
                args = data.get("args", {})
                tool = agent.tools.get(tool_name)

                if not tool:
                    raise ValueError(f"Tool '{tool_name}' not found on agent")
               
                # Invoke Tool
                console.print(f"[yellow]INVOKING TOOL: '{tool_name}' action '{action_name}' with args: {args}[/yellow]",style="bold black on yellow")
                tool_result = tool.invoke(action_name, args)
                tool_result_json = json.dumps(tool_result, indent=2)

                # Send the response back to the LLM 
                response = agent.run("Just list the name and. address of the user in plain text: " + tool_result_json)
                console.print(Panel.fit(response, title="Agent Response", border_style="green"))
            except:
                # treat as normal chat response
                console.print(Panel.fit(response, title="Agent Response", border_style="green"))
