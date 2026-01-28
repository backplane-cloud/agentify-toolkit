import click

@click.group()
def runtime_group():
    """Start Agent Runtime for Hosting Agents"""
    pass

@runtime_group.command("start")
@click.option("--port", default=8001, help="Port to run the Agentify runtime on")
def start_cmd(port):
    """Start the Agentify runtime server."""
    from agentify.runtime.server import start_runtime
    start_runtime(port=port)


@runtime_group.command("terminate")
@click.argument("agent_name", type=str)
@click.option("--server", default="http://127.0.0.1:8001", help="Runtime server URL")
def undeploy(agent_name, server):
    """Terminate a deployed Agent"""

    import requests
    try:
        resp = requests.delete(f"{server}/agents/{agent_name}/terminate")
        resp.raise_for_status()
        result = resp.json()
        if result.get("success"):
            click.echo(f"✓ Terminated agent: {agent_name}")
        else:
            click.echo(f"✗ Failed to terminate: {result.get('error','Unknown error')}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            click.echo(f"✗ Agent '{agent_name}' not found in runtime")
        else:
            click.echo(f"✗ Failed to contact runtime server: {e}")
    except Exception as e:
        click.echo(f"✗ Failed to contact runtime server at {server}: {e}")


@runtime_group.command("list")
@click.option("--server", default="http://127.0.0.1:8001", help="Runtime server URL")
def runtime_list(server):
    """List agents loaded on Agent Runtime"""
    import requests
    from ..cli_config import get_server
    url = server or get_server()
    if not url:
        click.echo("No server configured. Use 'agentify server set <url>'")
        return

    try:
        resp = requests.get(f"{url}/agents")
        resp.raise_for_status()
    except Exception as e:
        click.echo(f"Failed to contact runtime server at {url}: {e}")
        return

    agents = resp.json().get("agents", [])
    if not agents:
        click.echo("No agents loaded on the runtime server.")
        return

    click.echo(f"{'NAME':20} {'MODEL':15} {'PROVIDER':15} {'DESCRIPTION'}")
    click.echo("-" * 70)
    for a in agents:
        click.echo(f"{a['name']:<20} {str(a.get('model','')):<15} {str(a.get('provider','')):<15} {a.get('description','')}")


@runtime_group.command("invoke")
@click.argument("agent_name")
@click.option("--prompt", "-p", default=None, help="Prompt text for single request")
@click.option("--server", default=None, help="Override runtime server URL")
def runtime_invoke(agent_name, prompt, server):
    """Invoke agent with prompt --prompt"""

    import requests
    from ..cli_config import get_server

    url = server or get_server() or "http://127.0.0.1:8001"
    agent_endpoint = f"{url}/agents/{agent_name}/prompt"

    if prompt:
        try:
            resp = requests.post(agent_endpoint, json={"question": prompt})
            resp.raise_for_status()
            click.echo(f"{agent_name}: {resp.json().get('answer')}")
        except Exception as e:
            click.echo(f"Failed to invoke agent {agent_name}: {e}")
        return

    click.echo(f"Interactive session with agent '{agent_name}'. Type 'exit' or Ctrl+C to quit.")
    while True:
        try:
            question = click.prompt("You")
            if question.lower() in ("exit", "quit"):
                break
            resp = requests.post(agent_endpoint, json={"question": question})
            resp.raise_for_status()
            click.echo(f"{agent_name}: {resp.json().get('answer')}")
        except KeyboardInterrupt:
            click.e
