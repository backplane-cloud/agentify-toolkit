import click

@click.group("provider")
def provider_group():
    """Manage model providers and API keys"""
    pass


@provider_group.command("add")
@click.argument("provider_name")
def add_provider(provider_name):
    """Add/Update model provider API keys in .env"""
    from ..utils.env_manager import set_provider_key
    set_provider_key(provider_name)


@provider_group.command("list")
def list_provider():
    """Lists registered model providers"""

    from ..utils.env_manager import display_providers
    display_providers()


@provider_group.command("remove")
@click.argument("provider_name")
def remove_provider(provider_name):
    """Remove a model provider"""

    from ..utils.env_manager import remove_provider
    remove_provider(provider_name)

@provider_group.command("validate")
@click.argument("provider_name")
def validate_provider(provider_name):
    """Validate the Provider API key"""

    from ..utils.env_manager import validate_provider
    from rich.console import Console
    console = Console(force_terminal=True)

    try:
        with console.status(f"[yellow]Validating {provider_name}[/yellow]", spinner="dots", spinner_style="yellow"):
            result = validate_provider(provider_name)

        click.secho(f"✓ {provider_name} API KEY validated: {result}", fg="green")
        # click.secho(f"✓ {provider_name.upper()}_API_KEY validated", fg="green")

    except Exception as e:
        click.secho(f"✗ Validation failed: {e}", fg="red")
        raise SystemExit(1)
