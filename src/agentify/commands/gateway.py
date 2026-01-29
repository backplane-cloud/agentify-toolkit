import click
import uvicorn

@click.group(name="gateway")
def gateway_command():
    """Run the Agentify model gateway."""
    pass

@gateway_command.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
def start(host, port):
    """Start the model gateway server."""
    uvicorn.run(
        "agentify.gateway.server:app",
        host=host,
        port=port,
        reload=False
    )
