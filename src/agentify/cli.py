import click
from agentify import __version__
from .commands import (
    run_command,
    serve_command,
    deploy_command,
    runtime_group,
    tool_group,
    agent_group,
    provider_group
)

@click.group()
@click.version_option(version=__version__, prog_name="Agentify")
def main():
    """Agentify Toolkit CLI"""
    pass

# Attach lazy-loaded commands
main.add_command(run_command)
main.add_command(serve_command)
main.add_command(deploy_command)
main.add_command(runtime_group)
main.add_command(tool_group)
main.add_command(agent_group)
main.add_command(provider_group)

if __name__ == "__main__":
    main()
