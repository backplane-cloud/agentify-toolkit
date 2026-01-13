# Copyright 2026 Backplane Software
# Licensed under the Apache License, Version 2.0
import requests
import click
from pathlib import Path
import yaml
import os

from agentify import __version__
from .specs import load_agent_specs
from .agents import create_agent, create_agents

from .cli_ui import show_agent_menu
from .cli_config import set_server, get_server, add_provider, remove_provider, list_providers
# from .runtime_client import list_agents, upload_agent, delete_agent

from .server import serve_agent
from .runtime import start_runtime, deploy_agents

@click.group()
@click.version_option(version=__version__, prog_name="Agentify")
def main():
    """
    Agentify: A Developer Toolkit for Building Declarative AI Agents

    Common commands:
    
    agentify agent create

    agentify run myagent.yaml 

    Use '--help' with any command for more details.
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
# Agent Runtime
# -----------------------------
@main.group()
def runtime():
    """Start Agent Runtime for Hosting Agents"""
    pass

import requests
import click
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
            click.echo(f"✓ Undeployed agent: {agent_name}")
        else:
            click.echo(f"✗ Failed to undeploy: {result.get('error', 'Unknown error')}")
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

@main.group()
def agent():
    """Manage and inspect AI agent YAML files."""
    pass

@agent.command("add")
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
    for s in specs:
        name = s.get("name", "Unnamed")
        desc = s.get("description", "")
        provider = s.get("model","").get("provider")
        model = s.get("model","").get("id")
        click.echo(f"{name:<20} {provider:<20} {model:<20} {desc}")



@agent.command("show")
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


@main.group()
def provider():
    """Add/Remote AI Provider API Keys"""
    pass

@provider.command("add")
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

@provider.command("list")
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



@provider.command("remove")
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
