from datetime import datetime
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from expense_tracker.database.database import DatabaseManager

app = typer.Typer()


def _resolve_target_date(year: int | None, month: int | None) -> tuple[int, int]:
    """Validate that year and month are provided together, defaulting to today."""
    if (year is None) != (month is None):
        raise typer.BadParameter("Both --year and --month must be provided together.")

    target_year = year if year is not None else datetime.now().year
    target_month = month if month is not None else datetime.now().month

    return (target_year, target_month)


@app.command()
def set(
    ctx: typer.Context,
    budget: Annotated[float, typer.Argument(help="The budget amount to set.", min=0)],
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
            help="The month for the budget [1-12]",
            rich_help_panel="Date Arguments",
            min=1,
            max=12,
        ),
    ] = None,
) -> None:
    """Set or update the budget for a specific month and year

    Defaults to the currrent month and year if neither is provided. Both --year
    and --month must be specified together if setting or updating manually.
    """

    target_year, target_month = _resolve_target_date(year=year, month=month)

    db: DatabaseManager = ctx.obj["db"]
    console: Console = ctx.obj["console"]

    result = db.set_budget(year=target_year, month=target_month, amount=budget)
    if not result:
        console.print("[red]✖[/red] No budgets were updated.")
        raise typer.Exit()

    console.print(
        f"[bold green]✓[/bold green] Budget was successfully updated for [cyan]{target_year}/{target_month}[/cyan]"
    )


@app.command()
def list(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="Filter budgets by a specific year.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
    month: Annotated[
        int | None,
        typer.Option(
            "--month",
            "-m",
            help="Filter budgets by a specific month.",
            rich_help_panel="Date Arguments",
            min=1,
            max=12,
        ),
    ] = None,
) -> None:
    """List all recorded budgets.

    Optionally filter results by year and/or month.
    """

    db: DatabaseManager = ctx.obj["db"]
    console: Console = ctx.obj["console"]
    budgets = db.get_all_budgets(year=year, month=month)

    if not budgets:
        console.print("i [dim]No budgets found in the database.[/dim]")
        raise typer.Exit()

    table = Table(title="Budgets", box=box.ROUNDED)

    # Format: (column_name, style)
    columns = [
        ("ID", "cyan"),
        ("Year", "cyan"),
        ("Month", "cyan"),
        ("Amount", "green"),
    ]
    for column_name, style in columns:
        table.add_column(column_name, style=style)

    for dict_row in budgets:
        rows = [str(row) for row in dict_row.values()]
        table.add_row(*rows)

    console.print(table)


@app.command()
def remove(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="The year of the budget to delete.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
    month: Annotated[
        int | None,
        typer.Option(
            "--month",
            "-m",
            help="The month of the budget to delete",
            rich_help_panel="Date Arguments",
            min=1,
            max=12,
        ),
    ] = None,
) -> None:
    """Delete the budget for a specific year and month.

    Defaults to the current month and year if neither is provided. Both --year
    and --month must be specified together if removing manually.
    """

    target_year, target_month = _resolve_target_date(year=year, month=month)

    db: DatabaseManager = ctx.obj["db"]
    console: Console = ctx.obj["console"]

    result = db.delete_budget(year=target_year, month=target_month)
    if not result:
        console.print(
            f"[yellow]![/yellow] No budget found to remove for [cyan]{target_year}/{target_month}[/cyan]"
        )
        raise typer.Exit()
    console.print(
        f"[red]-[/red] Budget was successfully removed for [cyan]{target_year}/{target_month}[/cyan]"
    )


if __name__ == "__main__":
    app()
