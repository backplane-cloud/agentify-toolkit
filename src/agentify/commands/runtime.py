import click

@click.group()
def runtime_group():
    """Host Agentify Agent Runtime"""
    pass

@runtime_group.command("start")
@click.option("--port", default=8001, help="Port to run the Agentify runtime on")
def start_cmd(port):
    """Start the Agentify runtime server"""
    from agentify.runtime.server import start_runtime
    start_runtime(port=port)


@runtime_group.command("remove")
@click.argument("agent_name", type=str)
@click.option("--server", default="http://127.0.0.1:8001", help="Runtime server URL")
def undeploy(agent_name, server):
    """Remove a deployed Agent"""

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

    # from rich.table import Table
    # from rich.console import Console

    # console = Console()

    # table = Table(title="Agents")

    # table.add_column("Name", style="bold cyan", width=20)
    # table.add_column("Model", width=20)
    # table.add_column("Provider", width=20)
    # table.add_column("Tokens (In)", justify="right", style="yellow")
    # table.add_column("Tokens (Out)", justify="right", style="yellow")
    # table.add_column("Token Cost", justify="right", style="red")

    # for agent in agents:
    #     tokens = agent.get("input_tokens", 0) + agent.get("output_tokens", 0)
    #     style = "on red" if tokens > 1000 else None
    #     table.add_row(
    #         agent["name"],
    #         str(agent.get("model", "")),
    #         str(agent.get("provider", "")),
    #         str(agent.get("input_tokens", "")),
    #         str(agent.get("output_tokens", "")),
    #         str(agent.get("token_cost", "")),
    #         style=style
    #     )

    # console.print(table)
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    import requests
    import time

    console = Console()

    def build_table(agents):
        table = Table(title="Agent Runtime")

        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Model")
        table.add_column("Provider")
        table.add_column("Tokens In", justify="right", style="yellow")
        table.add_column("Tokens Out", justify="right", style="yellow")
        table.add_column("Token Cost", justify="right")

        spinner_frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        frame = int(time.time() * 10) % len(spinner_frames)

        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0
        for agent in agents:
            in_tokens = agent.get("input_tokens", 0)
            out_tokens = agent.get("output_tokens", 0)
            cost_tokens = agent.get("token_cost", 0)

            total_input_tokens += in_tokens
            total_output_tokens += out_tokens
            total_cost += cost_tokens

            if agent.get("active"):
                name = f"[black on yellow]{agent.get('name')}[/]"
                # status = "[green]RUNNING[/]"
                status = f"[green]{spinner_frames[frame]} RUNNING[/]"
                model = f"[green]{agent.get('model')}[/]"
                provider = f"[green]{agent.get('provider')}[/]"
                input_tokens = f"[green]{str(round(agent.get("input_tokens"), 6))}[/]"
                output_tokens = f"[green]{str(round(agent.get("output_tokens"), 6))}[/]"
                cost = f"[green]{str(round(agent.get("token_cost"), 6))}[/]"
            else:
                name = agent.get("name")
                status = "[dim]idle[/]"
                model = agent.get("model")
                provider = agent.get("provider")
                input_tokens = f"[dim]{str(round(agent.get("input_tokens"), 6))}[/]"
                output_tokens = f"[dim]{str(round(agent.get("output_tokens"), 6))}[/]"
                cost = f"[dim]{str(round(agent.get("token_cost"), 6))}[/]"
              

            table.add_row(
                name,
                status,
                provider,
                model,
                input_tokens,
                output_tokens,
                cost
            )

        table.add_section()
        table.add_row(
            "[bold]TOTAL[/]",
            "",
            "",
            "",
            f"[bold yellow]{round(total_input_tokens, 6)}[/]",
            f"[bold yellow]{round(total_output_tokens, 6)}[/]",
            f"[bold red]{round(total_cost, 6)}[/]",
        )


        return table


    with Live(console=console, refresh_per_second=2) as live:
        while True:
            try:
                resp = requests.get(f"{server}/agents")
                resp.raise_for_status()
                agents = resp.json().get("agents", [])
            except Exception as e:
                console.print(f"[red]Failed to fetch agents: {e}[/]")
                agents = []

            live.update(build_table(agents))
            time.sleep(0.5)

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
