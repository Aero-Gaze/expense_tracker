from datetime import datetime
from typing import Annotated

import typer

from expense_tracker.database.Database import DatabaseManager

app = typer.Typer()


@app.command()
def set(
    ctx: typer.Context,
    budget: Annotated[
        int, typer.Argument(help="The budget amount for the month", min=0)
    ],
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="The year for the budget",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
    month: Annotated[
        int | None,
        typer.Option(
            "--month",
            "-m",
            help="The month for the budget",
            rich_help_panel="Date Arguments",
            min=1,
            max=12,
        ),
    ] = None,
):
    """Set the budget for the particular year and month, defaults to current year and month"""

    if (year is None) != (month is None):
        raise typer.BadParameter("Both --year and --month must be provided together.")

    db: DatabaseManager = ctx.obj["db"]

    target_year = year if year is not None else datetime.now().year
    target_month = month if month is not None else datetime.now().month

    db.set_budget(year=target_year, month=target_month, amount=budget)

    typer.echo(f"Bugdet Successfully updated for {target_year}/{target_month}")


@app.command()
def list(
    ctx: typer.Context,
    year: Annotated[
        int | None, typer.Option("--year", "-y", help="The year to search")
    ] = None,
    month: Annotated[
        int | None,
        typer.Option("--month", "-m", help="The month to search", min=1, max=12),
    ] = None,
):
    """List all budgets (optionally filtered by year or month or both)."""

    db: DatabaseManager = ctx.obj["db"]
    budgets = db.get_all_budgets(year=year, month=month)

    if not budgets:
        typer.echo("No budgets found")
        return
    typer.echo(budgets)


if __name__ == "__main__":
    app()
