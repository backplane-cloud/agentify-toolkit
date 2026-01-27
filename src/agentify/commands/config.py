import click

@click.group()
def config_group():
    """View or manage Agentify configuration"""
    pass

@config_group.command("show")
def show():
    import json
    from ..cli_config import get_server
    click.echo(json.dumps({"server": get_server()}, indent=4))
