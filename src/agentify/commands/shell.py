import click
from agentify.shell.app import AgentifyApp

@click.command()
def shell_command():
    """Launch the Agentify Workbench (TUI)"""
    AgentifyApp().run()