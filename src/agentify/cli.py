# Copyright 2026 Backplane Software
# Licensed under the Apache License, Version 2.0
import requests
import click
from pathlib import Path
import yaml
import os

from agentify import __version__
from .specs import load_agent_specs, load_tool_spec, load_tool_specs
from .agents import create_agent, create_agents
from .tools import create_tool

from .cli_ui import show_agent_menu
from .cli_config import set_server, get_server, add_provider, remove_provider, list_providers
# from .runtime_client import list_agents, upload_agent, delete_agent
from agentify.utils.env_manager import set_provider_key, remove_provider, display_providers

from .server import serve_agent
from .runtime import start_runtime, deploy_agents

@click.group()
@click.version_option(version=__version__, prog_name="Agentify")
def main():
    """
    Agentify Toolkit is a developer-focused platform for building, running, and managing AI agents declaratively.
    """
    pass

# -----------------------------
# Run local agents (existing logic)
# -----------------------------
@main.command()
@click.argument("path", required=False)
@click.option("--model", type=str, help="Override the model ID at runtime")
@click.option("--provider", type=str, help="Override the LLM provider at runtime")
@click.option("--server", type=str, help="Optional: run on a remote server instead of local")
def run(path, provider, model, server):
    """
    Run an agent from a YAML file or directory.

    - Single: `agentify run agent.yaml`
    - Folder: shows interactive agent picker
    """
    # Determine target path
    agent_path = path or "./agents"
    path = Path(agent_path)
    click.echo(f"Loading agents from: {path}")

    # If server override is provided, run via runtime API
    if server:
        if not path.is_file():
            raise click.BadParameter("Remote run currently only supports a single YAML file")
        resp = upload_agent(server, str(path))
        click.echo(f"Agent uploaded and executed on server {server}: {resp}")
        return

    # ----- Local / programmatic agent logic -----
    if path.is_file():
        # Load YAML File
        with open(path, "r") as f:
            spec = yaml.safe_load(f)

        agent = create_agent(spec, provider=provider, model=model)

        # Load Tools into Agent if available
        if agent.tool_names:
            for tool_name in agent.tool_names:
                tool_path = f"examples/agents/tools/{tool_name}.yaml"
                tool_spec = load_tool_spec(tool_path)
                tool = create_tool(tool_spec)
                agent.tools[tool.name] = tool

        agent.chat()

    elif path.is_dir():
        # Multi-agent mode
        specs = load_agent_specs(path)
        agents = create_agents(specs)
        agent = show_agent_menu(agents)
        agent.chat()
    else:
        raise click.BadParameter(f"Path does not exist: {path}")


@main.command()
@click.argument("path")
@click.option("--port", type=int, help="Set server port e.g. 8001")
def serve(path, port):
    """
    Serve an agent locally via HTTP API and Web UI

    This launches a FastAPI server that exposes the agent over:
    - Web UI at    http://127.0.0.1:<port>
    - REST API at  /ask  /prompt  /info

    If --port is not provided, the default port is 8001.

    Examples:
    agentify serve agent.yaml
    agentify serve agent.yaml --port 8080

    """
    p = Path(path)
    if not p.is_file():
        raise click.BadParameter(f"{path} is not a valid agent file")

    with open(p, "r") as f:
        spec = yaml.safe_load(f)

    agent = create_agent(spec)
    serve_agent(agent, port=port)


# -----------------------------
# Agent Runtime
# -----------------------------
@main.group()
def runtime():
    """Start Agent Runtime for Hosting Agents"""
    pass

from .cli_config import get_server

# Ensure you already have the runtime group
@main.group()
def runtime():
    """Start Agent Runtime for Hosting Agents"""
    pass

@runtime.command("terminate")
@click.argument("agent_name", type=str)
@click.option("--server", default="http://127.0.0.1:8001", help="Runtime server URL")
def undeploy(agent_name, server):
    """
    Terminate an agent from the running Agentify Runtime.
    
    Example:
      agentify runtime terminate my-agent
    """
    try:
        resp = requests.delete(f"{server}/agents/{agent_name}/terminate")
        print(f"{server}/agents/{agent_name}/terminate")
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("success"):
            click.echo(f"✓ Terminated agent: {agent_name}")
        else:
            click.echo(f"✗ Failed to terminate: {result.get('error', 'Unknown error')}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            click.echo(f"✗ Agent '{agent_name}' not found in runtime")
        else:
            click.echo(f"✗ Failed to contact runtime server: {e}")
    except Exception as e:
        click.echo(f"✗ Failed to contact runtime server at {server}: {e}")

@runtime.command("list")
@click.option("--server", default="http://127.0.0.1:8001", help="Runtime server URL")
def runtime_list(server):

    """List all agents loaded in the runtime server"""
    url = server or get_server()

    if not url:
        click.echo("No server configured. Use 'agentify server set <url>'")
        return

    try:
        resp = requests.get(f"{url}/agents")
    except Exception as e:
        click.echo(f"Failed to contact runtime server at {url}: {e}")
        return

    if resp.status_code != 200:
        click.echo(f"Runtime error: {resp.status_code} {resp.text}")
        return

    agents = resp.json().get("agents", [])
    if not agents:
        click.echo("No agents loaded on the runtime server.")
        return

    # Print table
    click.echo(f"{'NAME':20} {'MODEL':15} {'PROVIDER':15} {'DESCRIPTION'}")
    click.echo("-" * 70)
    for a in agents:
        click.echo(
            f"{a['name']:<20} {str(a.get('model','')):<15} {str(a.get('provider','')):<15} {a.get('description','')}"
        )


@runtime.command("invoke")
@click.argument("agent_name")
@click.option("--prompt", "-p", default=None, help="Prompt text for single request")
@click.option("--server", default=None, help="Override runtime server URL")
def runtime_invoke(agent_name, prompt, server):
    """
    Invoke a deployed agent on the runtime server.

    - Interactive REPL mode if --prompt is not provided
    - Single-shot mode if --prompt="..."
    
    Examples:
      agentify runtime invoke my_agent
      agentify runtime invoke my_agent --prompt "Hello!"
    """

    url = server or get_server() or "http://127.0.0.1:8001"
    agent_endpoint = f"{url}/agents/{agent_name}/prompt"

    if prompt:
        # Single-shot mode
        try:
            resp = requests.post(agent_endpoint, json={"question": prompt})
            resp.raise_for_status()
            answer = resp.json().get("answer")
            click.echo(f"{agent_name}: {answer}")
        except Exception as e:
            click.echo(f"Failed to invoke agent {agent_name}: {e}")
        return

    # Interactive REPL mode
    click.echo(f"Interactive session with agent '{agent_name}'. Type 'exit' or Ctrl+C to quit.")
    while True:
        try:
            question = click.prompt("You")
            if question.lower() in ("exit", "quit"):
                break

            resp = requests.post(agent_endpoint, json={"question": question})
            resp.raise_for_status()
            answer = resp.json().get("answer")
            click.echo(f"{agent_name}: {answer}")

        except KeyboardInterrupt:
            click.echo("\nExiting interactive session.")
            break
        except Exception as e:
            click.echo(f"Error: {e}")


@runtime.command()
@click.option("--port", type=int, help="Set server port e.g. 8001")
def start(port):
    """
    Start Agent Runtime 
    """
    start_runtime(port=port)


# -----------------------------
# DEPLOY
# -----------------------------
@main.command()
@click.argument("paths", type=str)
@click.option("--server", default="http://127.0.0.1:8001", help="Runtime server URL")
def deploy(paths, server):
    """
    Deploy one or more agents to a running Agentify Runtime.

    Examples:
      agentify deploy agent.yaml
      agentify deploy examples/agents/
      agentify deploy examples/agents/agent1.yaml,agent2.yaml
    """

    # Split comma-separated paths (allow single file/folder too)
    raw_paths = [p.strip() for p in paths.split(",") if p.strip()]
    if not raw_paths:
        click.echo("Please provide at least one file or folder path.")
        return

    yaml_files = []

    # Iterate over paths, expand folders into YAML files
    for path_str in raw_paths:
        p = Path(path_str)
        if p.is_file() and p.suffix in (".yaml", ".yml"):
            yaml_files.append(p)
        elif p.is_dir():
            yaml_files.extend(__builtins__['list'](p.glob("*.yaml")) + __builtins__['list'](p.glob("*.yml")))
        else:
            click.echo(f"Skipping invalid path: {p}")

    if not yaml_files:
        click.echo("No YAML agent files found.")
        return

    # Transform YAML files to JSON specs
    agent_specs = []
    for file in yaml_files:
        try:
            with open(file, "r") as f:
                agent_specs.append(yaml.safe_load(f))
        except Exception as e:
            click.echo(f"Failed to load {file}: {e}")

    if not agent_specs:
        click.echo("No valid agent specs found.")
        return

    # Send to runtime server
    try:
        resp = requests.post(f"{server}/agents/add", json={"agents": agent_specs})
        resp.raise_for_status()
    except Exception as e:
        click.echo(f"Failed to contact runtime server at {server}: {e}")
        return

    loaded = resp.json().get("loaded", [])
    click.echo(f"✓ Deployed {len(loaded)} agent(s): {', '.join(loaded)}")


# -----------------------------
# TOOL
# -----------------------------

@main.group()
def tool():
    """Manage and inspect tool YAML files"""
    pass

# Plural for tools list
tool_alias = click.Group(
    name="tools", 
    commands=tool.commands, 
    hidden=True
)
main.add_command(tool_alias)

@tool.command("list")
@click.argument("path", required=False, default=".")
def list_tools(path):
    """
    List all tool YAML files in a directory.

    Example:
      agentify tool list ./examples/agents/tools
    """
    p = Path(path)
    if not p.is_dir():
        raise click.BadParameter(f"{path} is not a directory")

    specs = load_tool_specs(p)
    if not specs:
        click.echo("No tool YAML files found.")
        return

    click.echo(f"Found {len(specs)} tool(s) in {path}:")

       # Print table
    click.secho(f"{'NAME':15} {'DESCRIPTION':30} {'VENDOR':20} {'ENDPOINT'}", fg="cyan")
    click.echo("-" * 80)
    for s in specs:
        name = s.get("name", "Unnamed")
        description = s.get("description", "")
        vendor = s.get("vendor","")
        endpoint = s.get("endpoint","")
        
        click.echo(f"{name:<15} {description:<30} {vendor:<20} {endpoint}")

    click.secho(f"\nUse: agentify tool show <tool_name> for metadata", fg="yellow")

@tool.command("show")
@click.argument("tool_name_or_file", required=True)
def show_agent(tool_name_or_file):
    """
    Show details of a single tool

    Usage:

      agentify tool show tool.yaml\n

      agentify tool show <tool_name>
    """

    p = Path(tool_name_or_file)

    # If user passed bare name (no extension), add ".yaml"
    if p.suffix == "":
        p = p.with_suffix(".yaml")

    # Optional: if the file isn't found locally, look in ./agents or ./examples
    search_paths = [Path("."), Path("./tools"), Path("./examples/agents/tools")]

    resolved = None
    for base in search_paths:
        candidate = base / p
        if candidate.is_file():
            resolved = candidate
            break

    if not resolved:
        raise click.BadParameter(f"Tool file '{p}' not found in: {', '.join(str(sp) for sp in search_paths)}")

    with open(resolved, "r") as f:
        spec = yaml.safe_load(f)

    click.echo(f"Name           : {spec.get('name', 'Unnamed')}")
    click.echo(f"Version         : {spec.get('version', 'N/A')}")
    click.echo(f"Description    : {spec.get('description', '')}")
    click.echo(f"Vendor         : {spec.get('vendor', 'N/A')}")
    click.echo(f"Endpoint       : {spec.get('endpoint', '')}")
    actions = spec.get("actions", {})
    click.echo(f"Actions:")
    for name, action in actions.items():
        method = action.get("method", "N/A")
        path = action.get("path", "")
        click.secho(f"  --> {name} [{method} {path}]", fg="red")


# -----------------------------
# AGENT
# -----------------------------


@main.group()
def agent():
    """Manage and inspect agent YAML files."""
    pass

# Plural for tools list
agent_alias = click.Group(
    name="agents", 
    commands=agent.commands, 
    hidden=True
)
main.add_command(agent_alias)


@agent.command("new")
@click.argument("folder", required=False)
def create_agent_cli(folder):
    """
    Interactively create a new agent YAML file.

    Prompts for name, description, version, provider, model, role, and API key env.
    The file will be saved as <name>.yaml in the specified folder.
    """
    click.echo("Creating a new agent YAML...\n")

    # Prompt for basic info
    name = click.prompt("Agent Name")
    description = click.prompt("Description", default="")
    version = click.prompt("Version", default="0.1.0")
    
    # Model/provider info
    provider = click.prompt("Provider (e.g., openai, anthropic, xai, google, bedrock)")
    model_id = click.prompt("Model ID")
    api_key_env = click.prompt("API key environment variable name", default=f"{provider.upper()}_API_KEY")
    
    # Role
    click.echo("Define the agent's role. Use multiple lines if needed. Enter + Ctrl+D (Linux/macOS) or Enter + Ctrl+Z (Windows)")
    role_lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        role_lines.append(line)
    role = "\n".join(role_lines).strip()

    # Build agent spec
    agent_spec = {
        "name": name,
        "description": description,
        "version": version,
        "model": {
            "provider": provider,
            "id": model_id,
            "api_key_env": api_key_env
        },
        "role": role
    }

    # Ensure folder exists
    folder_path = Path(folder or ".")
    folder_path.mkdir(parents=True, exist_ok=True)

    # Sanitize filename
    filename = f"{name}.yaml"
    file_path = folder_path / filename

    # Save YAML
    with open(file_path, "w") as f:
        yaml.dump(agent_spec, f, sort_keys=False)

    click.echo(f"\nAgent YAML saved to {file_path}")

agent.add_command(create_agent_cli, name="create")
create_alias = click.Command(
    name="create",
    callback=create_agent_cli,
    hidden=True,
    help=create_agent_cli.help,
)
agent.add_command(create_alias)

@agent.command("list")
@click.argument("path", required=False, default=".")
def list_agents(path):
    """
    List all agent YAML files in a directory.

    Example:
      agentify agents list ./examples/agents
    """
    p = Path(path)
    if not p.is_dir():
        raise click.BadParameter(f"{path} is not a directory")

    specs = load_agent_specs(p)
    if not specs:
        click.echo("No agent YAML files found.")
        return

    click.echo(f"Found {len(specs)} agent(s) in {path}:")

       # Print table
    click.secho(f"{'NAME':20} {'PROVIDER':20} {'MODEL':20} {'DESCRIPTION'}", fg="cyan")
    click.echo("-" * 80)
    for s in specs:
        name = s.get("name", "Unnamed")
        desc = s.get("description", "")
        provider = s.get("model","").get("provider")
        model = s.get("model","").get("id")
        click.echo(f"{name:<20} {provider:<20} {model:<20} {desc}")

    click.secho(f"\nUse: agentify agent show <agent_name> for metadata", fg="yellow")



@agent.command("show")
@click.argument("agent_name_or_file", required=True)
def show_agent(agent_name_or_file):
    """
    Show details of a single agent

    Usage:

      agentify agent show agent.yaml\n

      agentify agent show <agent_name>
    """

    p = Path(agent_name_or_file)

    # If user passed bare name (no extension), add ".yaml"
    if p.suffix == "":
        p = p.with_suffix(".yaml")

    # Optional: if the file isn't found locally, look in ./agents or ./examples
    search_paths = [Path("."), Path("./agents"), Path("./examples/agents")]

    resolved = None
    for base in search_paths:
        candidate = base / p
        if candidate.is_file():
            resolved = candidate
            break

    if not resolved:
        raise click.BadParameter(f"Agent file '{p}' not found in: {', '.join(str(sp) for sp in search_paths)}")

    with open(resolved, "r") as f:
        spec = yaml.safe_load(f)

    click.echo(f"Name       : {spec.get('name', 'Unnamed')}")
    click.echo(f"Description: {spec.get('description', '')}")
    click.echo(f"Version    : {spec.get('version', 'N/A')}")
    click.echo(f"Role       : {spec.get('role', '').strip()}")
    model = spec.get("model", {})
    click.echo(f"Model      : {model.get('id', 'N/A')} ({model.get('provider', '')})")
    click.echo(f"Tools       : {spec.get('tools', '')}")





# -----------------------------
# Server configuration
# -----------------------------
@main.group(hidden=True)
def server():
    """Manage default runtime server configuration"""
    pass

@server.command("set")
@click.argument("url")
def server_set(url):
    """Set the default runtime server"""
    set_server(url)

@server.command("show")
def server_show():
    """Show the current default runtime server"""
    url = get_server()
    if url:
        click.echo(f"Default server: {url}")
    else:
        click.echo("No server configured.")

@main.group(hidden=True)
def config():
    """View or manage Agentify configuration"""
    pass

@config.command("show")
def config_show():
    """Show current Agentify configuration"""
    import json
    from agentify.cli_config import get_server

    config_data = {
        "server": get_server()
    }

    click.echo(json.dumps(config_data, indent=4))


@main.group(hidden=False)
def provider():
    """Add/Remove Model Providers"""
    pass

@provider.command("add")
@click.argument("provider_name")
def add_provider(provider_name):
    """
    Adds or updates provider API keys in .env
    """
    set_provider_key(provider_name)

@provider.command("list")
def list_provider():
    display_providers()


@provider.command("remove")
@click.argument("provider_name")
def remove_provider_cmd(provider_name):
    remove_provider(provider_name)
    


if __name__ == "__main__":
    main()
