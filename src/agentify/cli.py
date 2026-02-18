import click
from agentify import __version__
from .commands import (
    run_command,
    serve_command,
    deploy_command,
    gateway_command,
    runtime_group,
    tool_group,
    agent_group,
    provider_group,
    mcp_group, 
    xmcp_group
)

from rich.console import Console
from rich.panel import Panel

console = Console()

agentify_icon = """
[magenta] █████████████████[/magenta]    [yellow]agentify provider add <provider_name>[/yellow] [green]# e.g. openai, xai, anthropic[/green]
[magenta]░███▒▒▒▒███▒▒▒▒███[/magenta]    [yellow]agentify agent new[/yellow] [green]# <-- Creates a new Agent[/green]
[magenta]░███░░  ███░░  ███[/magenta]    [green]# Run Agent[/green]
[magenta]░█████████████████[/magenta]    [yellow]agentify run agent.yaml[/yellow]
[magenta]░█████░░░░░░░█████[/magenta]    [green]# Start MCP Server[/green]                
[magenta]░█████████████████[/magenta]    [yellow]agentify mcp2 start[/yellow]    
[magenta]░░░██░░██░░██░░██ [/magenta]    [green]# Start Agent Runtime → Deploy Agent[/green]
[magenta]  ░██ ░██ ░██ ░██ [/magenta]    [yellow]agentify runtime start[/yellow] [green]→[/green] [yellow]agentify deploy agent.yaml[/yellow]
"""

console.print(Panel(agentify_icon, title=f"AGENTIFY TOOLKIT CLI v{__version__}", subtitle="Build, Run and deploy AI Agents declaratively", border_style="white"))


@click.group()
@click.version_option(version=__version__, prog_name="Agentify")
def main():
    """Agentify Toolkit CLI"""
    pass

# Attach lazy-loaded commands
main.add_command(run_command)
main.add_command(serve_command)
main.add_command(deploy_command)
main.add_command(gateway_command)
main.add_command(runtime_group)
main.add_command(tool_group)
main.add_command(agent_group)
main.add_command(provider_group)
main.add_command(mcp_group)
main.add_command(xmcp_group)


if __name__ == "__main__":
    main()
