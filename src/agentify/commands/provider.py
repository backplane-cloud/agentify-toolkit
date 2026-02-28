import click
from ..providers.rate_card import get_ratecard
from rich.console import Console
from rich.table import Table

console = Console()

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
    # from rich.console import Console
    # console = Console(force_terminal=True)

    try:
        with console.status(f"[yellow]Validating {provider_name}[/yellow]", spinner="dots", spinner_style="yellow"):
            result = validate_provider(provider_name)

        click.secho(f"✓ {provider_name} API KEY validated: {result}", fg="green")
        # click.secho(f"✓ {provider_name.upper()}_API_KEY validated", fg="green")

    except Exception as e:
        click.secho(f"✗ Validation failed: {e}", fg="red")
        raise SystemExit(1)


@provider_group.command("ratecard")
@click.argument("provider_name", required=False)
def get_provider_rate(provider_name):
    """Display provider rate card."""


    # If provider_name is None → get all
    ratecard = get_ratecard(provider_name)

    if not ratecard:
        console.print(f"[red]No rate card found for '{provider_name}'[/red]")
        return

    table_title = (
        f"{provider_name.upper()} Rate Card"
        if provider_name
        else "All Providers Rate Card"
    )

    table = Table(title=table_title)

    table.add_column("Provider", style="cyan", no_wrap=True)
    table.add_column("Model", style="white", no_wrap=True)
    table.add_column("Input ($/1M)", justify="right", style="green")
    table.add_column("Output ($/1M)", justify="right", style="magenta")

    # CASE 1: Specific provider (shape = { model: rates })
    if provider_name:
        for model, rates in ratecard.items():
            table.add_row(
                provider_name,
                model,
                f"{rates['input_rate']:.2f}",
                f"{rates['output_rate']:.2f}",
            )

    # CASE 2: All providers (shape = { provider: { model: rates } })
    else:
        for provider, models in ratecard.items():
            for model, rates in models.items():
                table.add_row(
                    provider,
                    model,
                    f"{rates['input_rate']:.2f}",
                    f"{rates['output_rate']:.2f}",
                )

    console.print(table)
