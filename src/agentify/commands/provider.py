import click

@click.group("provider")
def provider_group():
    """Add, remove, or list model providers and keys."""
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
