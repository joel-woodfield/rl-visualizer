import click
import uvicorn
from rlviz.server import *

@click.command()
@click.option("--host", default="127.0.0.1", help="Host to run the web server.")
@click.option("--port", default=8000, help="Port to run the web server.")
def run(host, port):
    """Starts the RLVisualizer web interface."""
    print(f"Running RLVisualizer at http://{host}:{port}")
    start_server(host, port)

if __name__ == "__main__":
    run()

