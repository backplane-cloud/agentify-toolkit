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
# from agentify.mcp_client import MCPClient
from agentify.mcp.client import MCPClientHTTP
import asyncio


@dataclass
class Agent:
    name: str
    description: str
    provider: str
    model_id: str
    
    role: str

    # State - need to move to State Object to keep Agent stateless
    # Let the Runtime handle state. Need to think this through. 
    input_tokens: int = 0
    output_tokens: int = 0
    token_cost: float = 0.0
    active: bool = False
    latency: float = 0.0

    version: Optional[str] = field(default="0.0.0")
    
    tool_names: list = field(default_factory=list)
    tools: dict = field(default_factory=dict)

    # mcp_client: Optional["MCPClientHTTP"] = None
    mcp_clients: list[MCPClientHTTP] = field(default_factory=list)

    agent_file: Path | None = None
    _tools_loaded: bool = field(default=False, init=False)

    conversation_history: list = field(default_factory=list)
    
    def _get_total_tokens(self):
        """Returns input_tokens + output_tokens"""
        return self.input_tokens + self.output_tokens
        

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
            tool = create_tool(spec, tool_file)          # your tool factory
            self.tools[tool.name] = tool

        self._tools_loaded = True

    def get_model(self) -> str:
        return self.model_id

    def get_tools(self) -> list[str]:
        return list(self.tools.keys())
    
    async def run_async(self, user_prompt: str) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run, user_prompt)
    
    def run(self, user_prompt: str, stream: bool = False) -> dict:
        from agentify.providers import run_openai, run_anthropic, run_google, run_bedrock, run_github, run_x, run_deepseek, run_mistral, run_ollama, run_ollama_local, run_gateway_http
        import time

        start = time.perf_counter()

        match self.provider.lower():
            case "openai":
                result = run_openai(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "anthropic":
                result = run_anthropic(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "google":
                result = run_google(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "bedrock":
                result = run_bedrock(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "github":
                result = run_github(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "agentify":
                result = run_gateway_http(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "xai":
                result = run_x(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "deepseek":
                result = run_deepseek(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "mistral":
                result = run_mistral(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "ollama":
                result = run_ollama(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case "ollama_local":
                result = run_ollama_local(self.model_id, user_prompt, stream=stream) # <-- STREAMING SUPPORT IMPLEMENTED
            case _:
                raise ValueError(f"Unsupported provider: {self.provider}")

        latency = (time.perf_counter() - start)

        result["latency"] = round(latency,2)

        return result

    def chat(self, debug: bool = False, toolprompt: bool = False, showstats: bool = False, stream: bool = False):
        from rich.console import Console, Group
        from rich.panel import Panel
        from rich.prompt import Prompt
        from rich.text import Text
        from rich.pretty import Pretty
        
        # Load Tools from local Files in tools/
        if self.tool_names and not self._tools_loaded:
            self.load_tools()

        # MCP Tool loader v2
        mcp_tools = []
        mcp_tool_names = []

        for client in self.mcp_clients:
            client.initialize()
            tools = client.list_tools()

            for tool in tools:
                namespaced_tool = tool.copy()

                original_name = tool["name"]
                namespaced_name = f"{client.name}.{original_name}"

                namespaced_tool["name"] = namespaced_name

                mcp_tools.append(namespaced_tool)
                mcp_tool_names.append(namespaced_name)

        console = Console()
        
        # DISPLAY AGENT HEADER
        console.print(Panel(
            f"[bold cyan]{self.name.upper()}[/bold cyan] [dim]{self.version}[/dim]\n"
            f"Role: {self.role}\n"
            f"Using [yellow]{self.model_id}[/yellow] by {self.provider}\n"
            f"Agent Tools:      {self.tool_names}\n"
            f"MCP Server Tools: {mcp_tool_names}\n"
            f"Tool Prompt: {toolprompt}\n"
            f"Show Statistics: {showstats}\n"
            f"Streaming Mode: {stream}",
            border_style="cyan"
        ))

        
        # LOAD TOOL SCHEMAS
        tool_schemas = [tool.to_schema() for tool in self.tools.values()] if self.tools else None
        tools_block = ""
        if tool_schemas:
            # tools_block = "\n\nLOCAL TOOLS:\n" + json.dumps(tool_schemas, indent=2)
            tools_block = "\n\nLOCAL TOOLS:\n" + json.dumps(tool_schemas)

        # Load MCP Server Tools
        if self.mcp_clients:
            # tools_block += "\n\nMCP TOOLS:\n" + json.dumps(mcp_tools, indent=2)        
            tools_block += "\n\nMCP TOOLS:\n" + json.dumps(mcp_tools)        

        if debug:
            console.print(
                Panel.fit(
                    Group(
                        "[bold cyan]LOCAL TOOLS[/bold cyan]",
                        json.dumps(tool_schemas, indent=2, sort_keys=True) if tool_schemas else "[dim]None[/dim]",
                        "",
                        "[bold magenta]MCP TOOLS[/bold magenta]",
                        json.dumps(mcp_tools, indent=2, sort_keys=True) if self.mcp_clients else "[dim]None[/dim]"
                    ),
                    title="[bold white]Debug[/bold white]",
                    border_style="white",
                )
            )

        # Lightweight tool index for prompt (name + description only) // Reduces 'in' tokens
        tool_index = [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]
        mcp_tool_index = [
            {"name": tool["name"], "description": tool["description"]}
            for tool in mcp_tools
        ]
        index = tool_index + mcp_tool_index
        compact_index = json.dumps(index)
        
        # MAIN AGENTIC LOOP
        while True:
            prompt = Prompt.ask("\nEnter your prompt ('/exit' to quit)")
            if prompt.lower() in ["/exit", "quit", "q"]:
                console.print(f"[yellow]Total tokens used in this session:[/yellow] {self._get_total_tokens()}, Cost: {round(self.token_cost, 7)} USD")
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
            
                # Expensive sending Tool Schemas on each Prompt
                full_prompt += tools_block

                # TOKEN OPTIMISATION - Cheaper to send tool index
                # full_prompt += compact_index

            # TOKEN OPTIMISATION - Removing whitespace to compact prompt 
            import textwrap
            compact_prompt = " ".join(
                line.strip() for line in textwrap.dedent(full_prompt).splitlines() if line.strip()
            )
            
            # DEBUG: DISPLAY PROMPT SENT
            if debug:
                console.print(
                    Panel.fit(
                        Group(compact_prompt),
                        title=f"[bold white]Debug - Sent to {self.provider}/{self.model_id}[/bold white]",
                        border_style="white",
                    )
                )

            # Send prompt to model
            # with console.status(f"[green]{self.name.title()} is thinking...[/green]", spinner="dots"):
            #     response = self.run(compact_prompt)

            # NEW STREAMING MODE
            if stream: 
                console.print(f"[green]{self.name.title()} is thinking...[/green]")
                response = self.run(compact_prompt, stream=True)
                console.print()
            else:
                with console.status(f"[green]{self.name.title()} is thinking...[/green]", spinner="dots"):
                    response = self.run(compact_prompt)
                

        
            # Try parsing JSON (tool invocation)
            try:
                # Clean JSON      
                text = response.get("text") if isinstance(response, dict) else response
                cleaned = text.strip() if isinstance(text, str) else ""

                if cleaned.startswith('```'):                                                      
                    cleaned = cleaned.split('```')[1]                                              
                if cleaned.startswith('json'):                                                 
                    cleaned = cleaned[4:]                                                      
                    cleaned = cleaned.strip()     
    
                # LLM JSON RESPONSE
                data = json.loads(cleaned)
                tool_name = data.get("tool")
                action_name = data.get("action")
                args = data.get("args", {})
                tool = self.tools.get(tool_name)

                if toolprompt:
                    panel_content = Group(
                        Text(f"Tool: {tool_name}", style="white"),
                        Text("Arguments:"),
                        Pretty(args)
                    )
                    console.print(
                        Panel.fit(
                            panel_content,
                            title="[bold yellow]Tool Invocation Requested[/bold yellow]",
                            border_style="yellow",
                            style="on rgb(40,30,0)"
                        )
                    )
                    prompt = Prompt.ask("Do you Approve? (y/n)", default="n")

                    if prompt.lower() in ["n", "no"]:
                        response = "Tool Invocation was cancelled"
                    else:
                        if tool:
                            # TOOL HANDLING
                            if tool.type == "internal":
                                # Local Function Tool
                                console.print(f"USING LOCAL TOOL: '{tool_name}' with args: {args}", style="white on green")

                                # Note: Need to call LLM with Tool Schema to obtain the proper invocation Args

                                tool_result = tool.invoke(args=args)
                            else: 
                                # Local API Tool
                                console.print(f"USING LOCAL TOOL: '{tool_name}' action '{action_name}' with args: {args}", style="bold black on yellow")

                                # Note: Need to call LLM with Tool Schema to obtain the proper invocation Args

                                tool_result = tool.invoke(action_name, args)
                        else: 
                            # Check MCP
                            if tool_name in mcp_tool_names:
                                # MCP SERVER TOOL
                                console.print(f"USING MCP SERVER TOOL: '{tool_name}' with args: {args}", style="bold black on yellow")
                                # tool_result = self.mcp_client.call_tool(tool_name, args)
                                server_name, actual_tool = tool_name.split(".", 1)

                                client = next(
                                    (c for c in self.mcp_clients if c.name == server_name),
                                    None
                                )

                                if not client:
                                    raise Exception(f"No MCP client found for server '{server_name}'")

                                # Note: Need to call LLM with Tool Schema to obtain the proper invocation Args

                                tool_result = client.call_tool(actual_tool, args)

                        # Minify JSON to avoid confusing model in next prompt
                        tool_result_str = json.dumps(tool_result, separators=(',', ':'))

                        # Add tool output to conversation history
                        self.conversation_history.append({"role": "tool", "content": tool_result_str})

                        # Ask model to display tool output naturally
                        analysis_prompt = "Display the following tool data in natural language:\n" + tool_result_str
                        with console.status(f"{self.name.title()} is synthesising tool response...", spinner="dots"):
                            response = self.run(analysis_prompt)

                        # Store agent response in history
                        if isinstance(response, dict):
                            self.conversation_history.append(
                                {"role": "agent", "content": response["text"]}
                            )
                        else:
                            self.conversation_history.append(
                                {"role": "agent", "content": response}
                            )
                    
                else:
                    if tool:
                        # TOOL HANDLING
                        if tool.type == "internal":
                            # Local Function Tool
                            console.print(f"USING LOCAL TOOL: '{tool_name}' with args: {args}", style="white on green")

                            # Note: Need to call LLM with Tool Schema to obtain the proper invocation Args

                            tool_result = tool.invoke(args=args)
                        else: 
                            # Local API Tool
                            console.print(f"USING LOCAL TOOL: '{tool_name}' action '{action_name}' with args: {args}", style="bold black on yellow")

                            # Note: Need to call LLM with Tool Schema to obtain the proper invocation Args

                            tool_result = tool.invoke(action_name, args)
                    else: 
                        # Check MCP
                        if tool_name in mcp_tool_names:
                            # MCP SERVER TOOL
                            console.print(f"USING MCP SERVER TOOL: '{tool_name}' with args: {args}", style="bold black on yellow")
                            # tool_result = self.mcp_client.call_tool(tool_name, args)
                            server_name, actual_tool = tool_name.split(".", 1)

                            client = next(
                                (c for c in self.mcp_clients if c.name == server_name),
                                None
                            )

                            if not client:
                                raise Exception(f"No MCP client found for server '{server_name}'")

                            # Note: Need to call LLM with Tool Schema to obtain the proper invocation Args

                            tool_result = client.call_tool(actual_tool, args)

                    # Minify JSON to avoid confusing model in next prompt
                    tool_result_str = json.dumps(tool_result, separators=(',', ':'))

                    # Add tool output to conversation history
                    self.conversation_history.append({"role": "tool", "content": tool_result_str})

                    # Ask model to display tool output naturally
                    analysis_prompt = "Display the following tool data in natural language:\n" + tool_result_str
                    with console.status(f"{self.name.title()} is synthesising tool response...", spinner="dots"):
                        response = self.run(analysis_prompt)

                    # Store agent response in history
                    # self.conversation_history.append({"role": "agent", "content": response})
                    if isinstance(response, dict):
                        self.conversation_history.append(
                            {"role": "agent", "content": response["text"]}
                        )
                    else:
                        self.conversation_history.append(
                            {"role": "agent", "content": response}
                        )
                
                if isinstance(response, dict):
                    # Turn Token Usage
                    input_tokens = response["input_tokens"]
                    output_tokens = response["output_tokens"]
                    token_cost = response["token_cost"]
                    total = input_tokens + output_tokens
                    latency = response["latency"]


                    # Update Agent for cumulative input and output tokens
                    self.input_tokens += input_tokens
                    self.output_tokens += output_tokens
                    self.token_cost += token_cost
                    self.latency = latency

                    console.print(Panel.fit(response["text"], title="Agent Response", border_style="green"))
                    if showstats:
                        console.print(f"Latency (sec): {response["latency"]} Token Usage: In: {response["input_tokens"]} Out: {response["output_tokens"]} Total: {total} Session Total: {self._get_total_tokens()} Cost: {round(self.token_cost,7)} USD")
                else:
                    console.print(Panel.fit(response, title="Agent Response", border_style="green"))


            except (json.JSONDecodeError, ValueError):
                # Treat as normal chat response
                # self.conversation_history.append({"role": "agent", "content": response})
                if isinstance(response, dict):
                    self.conversation_history.append(
                        {"role": "agent", "content": response["text"]}
                    )
                else:
                    self.conversation_history.append(
                        {"role": "agent", "content": response}
                    )

                
                if isinstance(response, dict):
                    # Turn Token Usage
                    input_tokens = response["input_tokens"]
                    output_tokens = response["output_tokens"]
                    token_cost = response["token_cost"]
                    total = input_tokens + output_tokens
                    latency = response["latency"]

                    # Update Agent for cumulative input and output tokens
                    self.input_tokens += input_tokens
                    self.output_tokens += output_tokens
                    self.token_cost += token_cost
                    self.latency = latency

                    if not stream:
                        console.print(Panel.fit(response["text"], title="Agent Response", border_style="green"))
                    # console.print(f"Token Usage: In: {response["input_tokens"]} Out: {response["output_tokens"]} Total: {total} Session Total: {self._get_total_tokens()}")
                    # console.print(f"Token Usage: In: {response["input_tokens"]} Out: {response["output_tokens"]} Total: {total} Session Total: {self._get_total_tokens()} Cost: {round(self.token_cost,7)} USD")
                    if showstats:
                        console.print(f"Latency (sec): {response["latency"]} Token Usage: In: {response["input_tokens"]} Out: {response["output_tokens"]} Total: {total} Session Total: {self._get_total_tokens()} Cost: {round(self.token_cost,7)} USD")


                else:
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

    # Load MCP Server clients
    mcp_clients = []

    mcp_spec = spec.get("mcp", {})
    servers = mcp_spec.get("servers",[])

    for server in servers:
        server_name = server.get("name")
        endpoint = server.get("endpoint")

        if endpoint:
            client = MCPClientHTTP(
                name=server_name,
                endpoint=endpoint
            )
            mcp_clients.append(client)

    agent = Agent(name=name, provider=provider, model_id=model_id, role=role, description=description, version=version, tool_names=tool_names, agent_file=agent_file, mcp_clients=mcp_clients)

    return agent
