from typing import Annotated

import typer

from expense_tracker.database.Database import DatabaseManager

app = typer.Typer()


if __name__ == "__main__":
    app()
