# Copyright 2026 Backplane Software
# Licensed under the Apache License, Version 2.0

# from agentify import Agent
import os
from dataclasses import dataclass, field
from typing import Optional
import json




@dataclass
class Agent:
    name: str
    description: str
    provider: str
    model_id: str
    role: str
    version: Optional[str] = field(default="0.0.0")
    tool_names: list = field(default_factory=list)
    tools: dict = field(default_factory=dict)
    conversation_history: list = field(default_factory=list)

    def get_model(self) -> str:
        return self.model_id

    def get_tools(self) -> str:
        return self.tools.keys()
    
    def run(self, user_prompt: str) -> str:
        from agentify.providers import run_openai, run_anthropic, run_google, run_bedrock, run_x, run_deepseek, run_mistral, run_ollama, run_ollama_local, run_ollama_stream

        match self.provider.lower():
            case "openai":
                return run_openai(self.model_id, user_prompt)
            case "anthropic":
                return run_anthropic(self.model_id, user_prompt)
            case "google":
                return run_google(self.model_id, user_prompt)
            case "bedrock":
                return run_bedrock(self.model_id, user_prompt)
            case "xai":
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
        from rich.console import Console
        from rich.panel import Panel
        from rich.prompt import Prompt

        console = Console()
        
        # Print agent header
        console.print(Panel(
            f"[bold cyan]{agent.name.upper()}[/bold cyan] [dim]{agent.version}[/dim]\n"
            f"Role: {agent.description}\n"
            f"Using [yellow]{agent.model_id}[/yellow] by {agent.provider}\n"
            f"Tools: {agent.tool_names}",
            border_style="cyan"
        ))

        # Precompute tool schemas if any
        tool_schemas = [tool.to_schema() for tool in agent.tools.values()] if agent.tools else None
        tools_block = ""
        if tool_schemas:
            tools_block = "\n\nTOOLS:\n" + json.dumps(tool_schemas, indent=2)

        while True:
            prompt = Prompt.ask("\nEnter your prompt ('/exit' to quit)").strip()
            if prompt.lower() in ["/exit", "quit"]:
                console.print("[yellow]Exiting. Goodbye![/yellow]")
                break

            # Add user input to conversation history
            agent.conversation_history.append({"role": "user", "content": prompt})

            # Build full prompt from last N turns (e.g., last 6)
            full_prompt = f"You must assume the role of {agent.role} when responding to these prompts:\n\n"
            for turn in agent.conversation_history[-6:]:
                role = turn["role"]
                content = turn["content"]
                full_prompt += f"{role.upper()}: {content}\n"

            # Inject tool rules if tools exist
            if tool_schemas:
                full_prompt += """
                Rules for responding:

                1. Only produce JSON when a tool must be invoked. Do NOT include markdown (```json), code fences, or extra text.
                2. If the request can be answered naturally, respond in plain language.
                3. When producing JSON, follow this exact format:
                {
                    "tool": "<tool>",
                    "action": "<action>",
                    "args": {...}
                }
                4. Never hallucinate tool use. If unsure whether a tool is needed, respond in plain language.
                5. If asked to list available tools, respond in a single line: <toolname> <action> <args>. Do NOT use JSON or extra text.
                """
                full_prompt += tools_block

            # Send prompt to model
            with console.status(f"[blue]{agent.name} is thinking...[/blue]", spinner="dots"):
                response = agent.run(full_prompt)

            # Try parsing JSON (tool invocation)
            try:
                data = json.loads(response)
                tool_name = data.get("tool")
                action_name = data.get("action")
                args = data.get("args", {})

                tool = agent.tools.get(tool_name)
                if not tool:
                    raise ValueError(f"Tool '{tool_name}' not found on agent")

                # Invoke tool
                console.print(f"[yellow]INVOKING TOOL: '{tool_name}' action '{action_name}' with args: {args}[/yellow]", style="bold black on yellow")
                tool_result = tool.invoke(action_name, args)

                # Minify JSON to avoid confusing model in next prompt
                tool_result_str = json.dumps(tool_result, separators=(',', ':'))

                # Add tool output to conversation history
                agent.conversation_history.append({"role": "tool", "content": tool_result_str})

                # Ask model to display tool output naturally
                analysis_prompt = "Display the following tool data in natural language:\n" + tool_result_str
                with console.status(f"[blue]{agent.name} is analysing tool data...[/blue]", spinner="dots"):
                    response = agent.run(analysis_prompt)

                # Store agent response in history
                agent.conversation_history.append({"role": "agent", "content": response})
                console.print(Panel.fit(response, title="Agent Response", border_style="green"))


            except (json.JSONDecodeError, ValueError):
                # Treat as normal chat response
                agent.conversation_history.append({"role": "agent", "content": response})
                console.print(Panel.fit(response, title="Agent Response", border_style="green"))

def create_agents(specs: list) -> dict[str, Agent]:
    agents = {}
    for spec in specs:
        agent = create_agent(spec)
        agents[agent.name] = agent
    return agents

def create_agent(spec: dict, provider: str = None, model: str = None) -> Agent:
    """
    Create an Agent from a YAML/spec dictionary, optionally overriding model or provider.
    """
    name = spec.get("name")
    description = spec.get("description")
    version = spec.get("version")
    role = spec.get("role")

    model_spec = spec.get("model", {})
    model_id = model or model_spec.get("id")
    provider = provider or model_spec.get("provider")
    api_key_env = model_spec.get("api_key_env")

    if api_key_env:
        api_key = os.getenv(api_key_env)
    
    tool_names = spec.get("tools")

    agent = Agent(name=name, provider=provider, model_id=model_id, role=role, description=description, version=version, tool_names=tool_names)

    return agent
