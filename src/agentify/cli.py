# Copyright 2026 Backplane Software
# Licensed under the Apache License, Version 2.0

import click
from pathlib import Path
import yaml
import os

from agentify import __version__
from .specs import load_agent_specs
from .agents import create_agent, create_agents

from .cli_ui import show_agent_menu
from .cli_config import set_server, get_server, add_provider, remove_provider, list_providers
from .runtime_client import list_agents, upload_agent, delete_agent

from .server import serve_agent

@click.group()
@click.version_option(version=__version__, prog_name="Agentify")
def main():
    """
    Agentify: Declarative AI Agent Toolkit for Build & Experimentation

    Use Agentify to define agents in YAML and execute them locally, interactively or within a simple runtime server.
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
# List local agents (interactive)
# -----------------------------
@main.command()
@click.argument("path", required=False)
def list(path):
    """
    List agents in a folder and select one to run in chat mode
    """
    agent_path = path or "./agents"
    path = Path(agent_path)
    click.echo(f"Listing agents from: {path}")

    if not path.is_dir():
        raise click.BadParameter(f"Path is not a directory: {path}")

    specs = load_agent_specs(path)
    if not specs:
        click.echo("No agent YAML files found.")
        return

    agents = create_agents(specs)
    agent = show_agent_menu(agents)
    agent.chat()

@main.group()
def agents():
    """Manage and inspect AI agent YAML files."""
    pass

@agents.command("add")
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
    provider = click.prompt("Provider (e.g., openai, anthropic)")
    model_id = click.prompt("Model ID")
    api_key_env = click.prompt("API key environment variable name", default=f"{provider.upper()}_API_KEY")
    
    # Role
    click.echo("Define the agent's role. Use multiple lines if needed. End with Ctrl+D (Linux/macOS) or Ctrl+Z (Windows) and Enter.")
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

@agents.command("list")
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
    for s in specs:
        name = s.get("name", "Unnamed")
        desc = s.get("description", "")
        provider = s.get("model","").get("provider")
        model = s.get("model","").get("id")
        click.echo(f"{name:<20} {provider:<20} {model:<20} {desc}")



@agents.command("show")
@click.argument("agent_file", required=True)
def show_agent(agent_file):
    """
    Show details of a single agent YAML file.

    Example:
      agentify agents show ./examples/agents/agent1.yaml
    """
    p = Path(agent_file)
    if not p.is_file():
        raise click.BadParameter(f"{agent_file} is not a valid file")

    with open(p, "r") as f:
        spec = yaml.safe_load(f)

    # Pretty print key fields
    click.echo(f"Name       : {spec.get('name', 'Unnamed')}")
    click.echo(f"Description: {spec.get('description', '')}")
    click.echo(f"Version    : {spec.get('version', 'N/A')}")
    click.echo(f"Role       : {spec.get('role', '').strip()}")
    model = spec.get("model", {})
    click.echo(f"Model      : {model.get('id', 'N/A')} ({model.get('provider', '')})")




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


# -----------------------------
# Runtime server commands
# -----------------------------
@main.group(hidden=True)
def runtime():
    """Manage agents on a remote runtime server"""
    pass

@runtime.command("list")
@click.option("--server", default=None, help="Override default server URL")
def show_server_agents(server):
    """List agents running on the runtime server"""
    url = server or get_server()
    if not url:
        click.echo("No server configured. Use 'agentify server set <url>'")
        return

    agents = list_agents(url)
    click.echo(f"{'NAME':20} {'STATUS':10} {'PROVIDER':10} {'MODEL'}")
    for a in agents:
        click.echo(f"{a['name']:20} {a['status']:10} {a['provider']:10} {a['model']}")

@runtime.command("show")
@click.argument("agent_name")
@click.option("--server", default=None, help="Override default server URL")
def runtime_show(agent_name, server):
    """Show details of a specific agent on the runtime server"""
    url = server or get_server()
    if not url:
        click.echo("No server configured. Use 'agentify server set <url>'")
        return

    agent = list_agents(url, filter_name=agent_name)  # or implement get_agent_details(agent_name)
    if not agent:
        click.echo(f"Agent not found: {agent_name}")
        return

    # Print detailed info
    for a in agent:
        click.echo(f"Name: {a['name']}")
        click.echo(f"Status: {a['status']}")
        click.echo(f"Provider: {a['provider']}")
        click.echo(f"Model: {a['model']}")
        click.echo(f"Version: {a.get('version', 'N/A')}")
        click.echo("-" * 40)

@runtime.command("load")
@click.argument("path")
@click.option("--server", default=None, help="Override default server URL")
def upload(path, server):
    """Upload an agent YAML file to the runtime server"""
    url = server or get_server()
    if not url:
        click.echo("No server configured. Use 'agentify server set <url>'")
        return
    resp = upload_agent(url, path)
    click.echo(f"Uploaded {path} -> {url}: {resp}")


@runtime.command("delete")
@click.argument("agent_name")
@click.option("--server", default=None, help="Override default server URL")
def delete(agent_name, server):
    """Delete an agent from the runtime server"""
    url = server or get_server()
    if not url:
        click.echo("No server configured. Use 'agentify server set <url>'")
        return
    resp = delete_agent(url, agent_name)
    click.echo(f"Deleted {agent_name} from {url}: {resp}")

@main.group()
def providers():
    """Add/Remote AI Provider API Keys"""
    pass

@providers.command("add")
@click.argument("provider")
@click.option("--env", "env_var", help="Environment variable name")
@click.option("--key", help="API key (optional, will prompt if omitted)")
def providers_add(provider, env_var, key):
    """Add an AI Provider and API KEY"""

    provider = provider.lower()
    env_var = env_var or f"{provider.upper()}_API_KEY"

    if not key:
        key = click.prompt(
            f"Enter API key for {provider}",
            hide_input=True,
        )

    add_provider(provider, env_var)

    click.echo(f"✓ Provider '{provider}' added to local config\n")
    click.echo("To apply in your current shell, run:\n")
    click.echo(f"export {env_var}={key}")

@providers.command("list")
def providers_list():
    """List configured providers with their current status"""

    providers = list_providers()

    if not providers:
        click.echo("No providers configured.")
        return

    # click.echo("Configured providers:\n")
    # for name, cfg in providers.items():
    #     click.echo(f"• {name}")
    #     click.echo(f"  env: {cfg['env']}\n")

    click.echo("Configured providers:\n")
    for name, cfg in providers.items():
        env_var = cfg.get("env")
    
        # Check if the env var is present in the current shell
        if env_var in os.environ and os.environ[env_var]:
            loaded = click.style("READY", fg="green")  # green for ready
        else:
            loaded = click.style(
                f"MISSING - run command: agentify providers add {name}", fg="yellow"
            )  # yellow for not set

        click.echo(f"• {name}")
        click.echo(f"  env: {env_var}")
        click.echo(f"  status: {loaded}\n")



@providers.command("remove")
@click.argument("provider")
def providers_remove(provider):
    """Remove a configured providers"""

    env_var = remove_provider(provider)

    if not env_var:
        click.echo(f"Provider not found: {provider}")
        return

    click.echo(f"✓ Provider '{provider}' removed from config\n")
    click.echo("To remove from your current shell, run:\n")
    click.echo(f"unset {env_var}")


if __name__ == "__main__":
    main()
