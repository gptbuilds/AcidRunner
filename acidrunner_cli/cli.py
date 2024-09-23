from typing import Optional, Annotated

import asyncio
import typer

from acidrunner_cli.utils.config import load_runner
app = typer.Typer()

@app.command()
def run(
        config_file:  Optional[Annotated[str, typer.Option("--config-file", "-f", help="File to scan for configs")]] = None,
        runs: Annotated[int, typer.Option("--runs", "-r", help="Number of runs will override the amt of runs in the config file.")] = 1,
    ):
    print(42*"*")
    print(f"Amount of runs: {runs}")
    print(42*"*")
    runner = load_runner(config_file)
    runner.run(runs)

if __name__ == "__main__":
    app()
