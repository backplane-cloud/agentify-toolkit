# Copyright 2026 Backplane Software
# Licensed under the Apache License, Version 2.0

# from agentify import Agent
import os
from dataclasses import dataclass, field
from typing import Optional
import json
from .specs import load_tool_spec
from .tool import create_tool
from pathlib import Path

# Import MCP Client
from agentify.mcp_client import MCPClient


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

    mcp_client: Optional["MCPClient"] = None

    agent_file: Path | None = None
    _tools_loaded: bool = field(default=False, init=False)

    conversation_history: list = field(default_factory=list)

    def load_tools(self, tool_path_override: str | Path | None = None):
        """
        Load tools for this agent. 

        - Defaults to <agent_file parent>/tools
        - Optional override via tool_path_override
        - Users do not need to worry about paths
        """
        if self._tools_loaded:
            return

        # Determine tools directory
        if tool_path_override:
            tools_dir = Path(tool_path_override).resolve()
        elif self.agent_file:
            tools_dir = Path(self.agent_file).resolve().parent / "tools"
        else:
            # fallback only if agent_file not set
            tools_dir = Path.cwd() / "tools"

        if not tools_dir.exists():
            raise FileNotFoundError(f"Tools directory does not exist: {tools_dir}")

        # Load each tool
        self.tools = {}  # reset
        for tool_name in self.tool_names or []:
            tool_file = tools_dir / f"{tool_name}.yaml"
            if not tool_file.exists():
                raise FileNotFoundError(f"Tool '{tool_name}' not found at {tool_file}")

            spec = load_tool_spec(tool_file)  # your YAML loader
            tool = create_tool(spec)          # your tool factory
            self.tools[tool.name] = tool

        self._tools_loaded = True

    def get_model(self) -> str:
        return self.model_id

    def get_tools(self) -> list[str]:
        return list(self.tools.keys())
    
    def run(self, user_prompt: str) -> str:
        from agentify.providers import run_openai, run_anthropic, run_google, run_bedrock, run_github, run_x, run_deepseek, run_mistral, run_ollama, run_ollama_local, run_gateway_http

        match self.provider.lower():
            case "openai":
                return run_openai(self.model_id, user_prompt)
            case "anthropic":
                return run_anthropic(self.model_id, user_prompt)
            case "google":
                return run_google(self.model_id, user_prompt)
            case "bedrock":
                return run_bedrock(self.model_id, user_prompt)
            case "github":
                return run_github(self.model_id, user_prompt)
            case "agentify":
                return run_gateway_http(self.model_id, user_prompt)
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



    def chat(self, debug: bool = False):
        from rich.console import Console
        from rich.panel import Panel
        from rich.prompt import Prompt
        
        # Load Tools from local Files in tools/
        if self.tool_names and not self._tools_loaded:
            self.load_tools()

        # MCP Tool load
        # mcp_tool_names = [t["name"] for t in self.mcp_tools]
        mcp_tools = self.mcp_client.list_tools()
        mcp_tool_names = [t["name"] for t in mcp_tools]

        console = Console()
        
        # Print agent header
        console.print(Panel(
            f"[bold cyan]{self.name.upper()}[/bold cyan] [dim]{self.version}[/dim]\n"
            f"Role: {self.description}\n"
            f"Using [yellow]{self.model_id}[/yellow] by {self.provider}\n"
            f"Tools: {self.tool_names}\n"
            f"MCP Tools: {mcp_tool_names}",
            border_style="cyan"
        ))

        
        # Load Local Tool Schemas
        tool_schemas = [tool.to_schema() for tool in self.tools.values()] if self.tools else None
        tools_block = ""
        if tool_schemas:
            tools_block = "\n\nLOCAL TOOLS:\n" + json.dumps(tool_schemas, indent=2)

        # Load MCP Server Tools
        if self.mcp_client:
            tools_block += "\n\nMCP TOOLS:\n" + json.dumps(mcp_tools, indent=2)
            

        


        if debug:
            console.print(tools_block)

        while True:
            prompt = Prompt.ask("\nEnter your prompt ('/exit' to quit)")
            if prompt.lower() in ["/exit", "quit"]:
                console.print("[yellow]Exiting. Goodbye![/yellow]")
                break

            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})

            # Build full prompt from last N turns (e.g., last 6)
            full_prompt = f"You must assume the role of {self.role} when responding to these prompts:\n\n"
            for turn in self.conversation_history[-6:]:
                role = turn["role"]
                content = turn["content"]
                full_prompt += f"Conversation History\n {role.upper()}: {content}\n"

            # Inject tool rules if tools exist
            if tool_schemas:
                full_prompt += """
Respond to user requests naturally, but if a tool must be invoked, respond with ONLY raw JSON that is parseable, with no code fences, no extra labels, and no commentary.

Rules:

1. If the request is "list tools", respond with a numbered list of all tools in this pattern:
   1. <tool name>: <description>: <arguments>: <type> (local or remote)

2. When invoking a tool, respond ONLY with the JSON object in this exact format:
{
    "tool": "<tool name>",
    "action": "<action name>",
    "args": {...}
}
Do NOT wrap this in markdown, code blocks, backticks, or any extra text. The JSON must be parseable directly.

3. Only use a tool if necessary. If no tool is needed, respond in plain language.

4. Use the tool arguments exactly as defined in the schema.

When a user requests a tool action, produce only the JSON object following the above format.
                """
                full_prompt += tools_block
            
            if debug:
                console.print(full_prompt)

            # Send prompt to model
            with console.status(f"[blue]{self.name} is thinking...[/blue]", spinner="dots"):
                response = self.run(full_prompt)

            # Try parsing JSON (tool invocation)
            try:
                # Clean JSON                           
                cleaned = response.strip()                                                                                                                 
                if cleaned.startswith('```'):                                                      
                    cleaned = cleaned.split('```')[1]                                              
                if cleaned.startswith('json'):                                                 
                    cleaned = cleaned[4:]                                                      
                    cleaned = cleaned.strip()     
    
                data = json.loads(cleaned)              
                tool_name = data.get("tool")
                action_name = data.get("action")
                args = data.get("args", {})
                tool = self.tools.get(tool_name)

                if not tool:
                    # Check MCP
                    if tool_name in mcp_tool_names:
                        # MCP SERVER TOOL
                        console.print(f"INVOKING MCP SERVER TOOL: '{tool_name}' with args: {args}", style="bold black on yellow")
                        tool_result = self.mcp_client.invoke(tool_name, args)

                # if not tool:
                #     raise ValueError(f"Tool '{tool_name}' not found on agent")

                if tool:
                    # TOOL HANDLING
                    if tool.type == "internal":
                        # INTERNAL TOOL
                        console.print(f"INVOKING INTERNAL TOOL: '{tool_name}' with args: {args}", style="bold black on yellow")
                        tool_result = tool.invoke(args=args)
                    else: 
                        # REMOTE TOOL
                        console.print(f"INVOKING REMOTE TOOL: '{tool_name}' action '{action_name}' with args: {args}", style="bold black on yellow")
                        tool_result = tool.invoke(action_name, args)



                # Minify JSON to avoid confusing model in next prompt
                tool_result_str = json.dumps(tool_result, separators=(',', ':'))

                # Add tool output to conversation history
                self.conversation_history.append({"role": "tool", "content": tool_result_str})

                # Ask model to display tool output naturally
                analysis_prompt = "Display the following tool data in natural language:\n" + tool_result_str
                with console.status(f"[blue]{self.name} is analysing tool data...[/blue]", spinner="dots"):
                    response = self.run(analysis_prompt)

                # Store agent response in history
                self.conversation_history.append({"role": "agent", "content": response})
                console.print(Panel.fit(response, title="Agent Response", border_style="green"))


            except (json.JSONDecodeError, ValueError):
                # Treat as normal chat response
                self.conversation_history.append({"role": "agent", "content": response})
                console.print(Panel.fit(response, title="Agent Response", border_style="green"))

def create_agents(specs: list) -> dict[str, Agent]:
    agents = {}
    for spec in specs:
        agent = create_agent(spec)
        agents[agent.name] = agent
    return agents

def create_agent(spec: dict, provider: str = None, model: str = None, agent_file: Path | None = None) -> Agent:
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
    
    # Local Tools via tool.yaml or tool.yaml/tool.py within tools/
    tool_names = spec.get("tools")

    # MCP Tools via MCP Server http://localhost:3333
    mcp_tools = []
    mcp_spec = spec.get("mcp")
    if mcp_spec:
        endpoint = mcp_spec.get("endpoint")
        if endpoint:
            mcp_client = MCPClient(endpoint)


    agent = Agent(name=name, provider=provider, model_id=model_id, role=role, description=description, version=version, tool_names=tool_names, agent_file=agent_file, mcp_client=mcp_client)

    return agent
