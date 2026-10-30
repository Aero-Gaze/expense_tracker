from datetime import datetime
from typing import Annotated

import typer
from rich import box
from rich.table import Table

from expense_tracker.cli.app_state import AppState

app = typer.Typer(no_args_is_help=True)


def _resolve_target_date(year: int | None, month: int | None) -> tuple[int, int]:
    """Gets the year and month. Uses the current date if neither is provided."""

    # Check whether both year and month are provided
    if year is None and month is not None:
        raise typer.BadParameter("Both --year and --month must be provided together.")

    if month is None and year is not None:
        raise typer.BadParameter("Both --year and --month must be provided together.")

    # Use the current year if no year is provided
    if year is None:
        target_year = datetime.now().year
    else:
        target_year = year

    # Use the current month if no month is provided
    if month is None:
        target_month = datetime.now().month
    else:
        target_month = month

    return target_year, target_month


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
    """Set or update a budget for a specific month and year."""

    # Get the year and month
    target_year, target_month = _resolve_target_date(year, month)

    state: AppState = ctx.obj

    # Get the database and console
    db = state.budget
    console = state.console

    # Save the budget in the database
    result = db.set_budget(year=target_year, month=target_month, amount=budget)

    # Check whether the budget was saved
    if result is False:
        console.print("[red]✖[/red] No budgets were updated.")
        raise typer.Exit()

    console.print(
        f"[bold green]✓[/bold green] Budget was successfully updated "
        f"for [cyan]{target_year}/{target_month}[/cyan]"
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
    """Display all recorded budgets."""

    state: AppState = ctx.obj

    # Get the database and console
    db = state.budget
    console = state.console

    # Get budgets from the database
    budgets = db.get_budgets(year=year, month=month)

    # Check whether any budgets were found
    if not budgets:
        console.print("i [dim]No budgets found in the database.[/dim]")
        raise typer.Exit()

    # Create a Rich table
    table = Table(title="Budgets", box=box.ROUNDED)

    # Add table columns
    table.add_column("ID", style="cyan", justify="left")
    table.add_column("Year", style="cyan", justify="left")
    table.add_column("Month", style="cyan", justify="left")
    table.add_column("Amount", style="green", justify="right")

    # Add database records to the table
    for budget in budgets:
        budget_id = str(budget["id"])
        budget_year = str(budget["year"])
        budget_month = str(budget["month"])
        budget_amount = str(budget["amount"])

        table.add_row(budget_id, budget_year, budget_month, budget_amount)

    # Display the table
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
    """Delete a budget for a specific year and month."""

    # Get the year and month
    target_year, target_month = _resolve_target_date(year, month)

    state: AppState = ctx.obj

    # Get the database and console
    db = state.budget
    console = state.console

    # Delete the budget
    result = db.delete_budget(year=target_year, month=target_month)

    # Check whether the budget was deleted
    if result is False:
        console.print(
            f"[yellow]![/yellow] No budget found to remove "
            f"for [cyan]{target_year}/{target_month}[/cyan]"
        )
        raise typer.Exit()

    console.print(
        f"[red]-[/red] Budget was successfully removed "
        f"for [cyan]{target_year}/{target_month}[/cyan]"
    )


if __name__ == "__main__":
    app()
