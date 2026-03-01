# src/agentify/cli.py
import click
import importlib
from agentify import __version__
from rich.console import Console
from rich.panel import Panel

# --- Console & Banner (instant) ---
console = Console(force_terminal=True)
agentify_icon = """
[white]             ██   [/white]
[white] █████████████████[/white]    Command: [yellow]agentify provider add <provider_name>[/yellow] [green]# e.g. openai, xai, anthropic[/green]
[white]░██   ░░███   ░░██[/white]    Command: [yellow]agentify agent new[/yellow] [green]# <-- Creates a new Agent[/green]
[white]░██     ███     ██[/white]    [green]# Run Agent[/green]
[white]░█████████████████[/white]    Command: [yellow]agentify run agent.yaml[/yellow]
[white]░███████   ███████[/white]    [green]# Start MCP Server[/green]                
[white]░█████████████████[/white]    Command: [yellow]agentify mcp start[/yellow]    
[white]░░░██░░██░░██░░██ [/white]    [green]# Start Agent Runtime → Deploy Agent[/green]
[white]  ░██ ░██ ░██ ░██ [/white]    Command: [yellow]agentify runtime start[/yellow] [green]→[/green] [yellow]agentify deploy agent.yaml[/yellow]
[white]  ░░  ░░  ░░  ░░  [/white]
"""

COMMANDS = {
    "provider": {"target": "agentify.commands.provider:provider_group", "help": "Add, remove, or list AI providers (OpenAI, Anthropic, etc.)"},
    "agent": {"target": "agentify.commands.agent:agent_group", "help": "Create, inspect, and manage AI agents"},
    "run": {"target": "agentify.commands.run:run_command", "help": "Execute an agent from a YAML configuration file"},
    "serve": {"target": "agentify.commands.serve:serve_command", "help": "Start an HTTP server to run an agent interactively"},
    "deploy": {"target": "agentify.commands.deploy:deploy_command", "help": "Deploy an agent to a runtime or production environment"},
    "runtime": {"target": "agentify.commands.runtime:runtime_group", "help": "Launch and manage the agent runtime environment"},
    "gateway": {"target": "agentify.commands.gateway:gateway_command", "help": "Start the model gateway for routing AI requests"},
    "tool": {"target": "agentify.commands.tool:tool_group", "help": "Add, remove, or manage tools for agent use"},
    "mcp": {"target": "agentify.commands.mcp:mcp_group", "help": "Start and control the MCP server and associated services"},
}

# --- Lazy leaf command ---
class LazyCommand(click.Command):
    def __init__(self, module_path: str, attr_name: str, help_text: str = None):
        self.module_path = module_path
        self.attr_name = attr_name
        super().__init__(name=attr_name, help=help_text)
        # Allow extra arguments (must be set after __init__)
        self.allow_extra_args = True
        self.ignore_unknown_options = True  # Allows things like 'agent.yaml'

    def invoke(self, ctx):
        # Lazy import the actual command
        module = importlib.import_module(self.module_path)
        real_cmd = getattr(module, self.attr_name)

        if not isinstance(real_cmd, click.Command):
            raise click.ClickException(f"Command {self.attr_name} is not a Click Command")

        # Forward raw CLI args to the real command
        return real_cmd.main(args=ctx.args, standalone_mode=False)

# --- Lazy group command ---
class LazyGroupCommand(click.Group):
    """Lazy-loaded click.Group with subcommands."""
    def __init__(self, module_path: str, attr_name: str, help_text: str = None):
        self.module_path = module_path
        self.attr_name = attr_name
        super().__init__(name=attr_name, help=help_text)

    def list_commands(self, ctx):
        module = importlib.import_module(self.module_path)
        real_group = getattr(module, self.attr_name)
        return real_group.list_commands(ctx)

    def get_command(self, ctx, name):
        module = importlib.import_module(self.module_path)
        real_group = getattr(module, self.attr_name)
        return real_group.get_command(ctx, name)

# --- Lazy main group ---
class LazyMainGroup(click.Group):
    def list_commands(self, ctx):
        return COMMANDS.keys()

    def get_command(self, ctx, name):
        if name not in COMMANDS:
            return None
        module_path, attr_name = COMMANDS[name]["target"].split(":")
        help_text = COMMANDS[name].get("help", None)

        # If the attribute name ends with "_group", treat as LazyGroupCommand
        if attr_name.endswith("_group"):
            return LazyGroupCommand(module_path, attr_name, help_text)
        else:
            return LazyCommand(module_path, attr_name, help_text)

class LazyGroup(click.Group):
    def list_commands(self, ctx):
        return sorted(COMMANDS.keys())

    def get_command(self, ctx, name):
        if name not in COMMANDS:
            return None

        # Split module path and attribute
        module_path, attr_name = COMMANDS[name]["target"].split(":")
        help_text = COMMANDS[name].get("help")

        # Import module lazily
        module = importlib.import_module(module_path)
        cmd = getattr(module, attr_name)

        # Attach help if missing
        if help_text and getattr(cmd, "help", None) is None:
            cmd.help = help_text

        return cmd
    
# --- Main entrypoint ---
@click.group(cls=LazyMainGroup, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="Agentify")
@click.pass_context
def main(ctx):
    """Agentify Toolkit CLI"""
    # Show banner only if no subcommand is invoked
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                agentify_icon,
                title=f"AGENTIFY TOOLKIT CLI v{__version__}",
                subtitle="Build, Run and deploy AI Agents declaratively",
                border_style="white",
            )
        )
    
        click.echo()  # blank line
        click.echo(ctx.command.get_help(ctx))