import click
from pathlib import Path

@click.command("serve")
@click.argument("path")
@click.option("--port", type=int, help="Set server port e.g. 8001")
def serve_command(path, port):
    """Serve an agent locally via HTTP API and Web UI"""
    import yaml
    from ..agents import create_agent
    from ..server import serve_agent

    p = Path(path)
    if not p.is_file():
        raise click.BadParameter(f"{path} is not a valid agent file")

    with open(p, "r") as f:
        spec = yaml.safe_load(f)

    agent = create_agent(spec)
    serve_agent(agent, port=port)
