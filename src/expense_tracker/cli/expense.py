from datetime import datetime
from typing import Annotated

import typer
from rich import box
from rich.table import Table

from expense_tracker.cli.app_state import AppState

app = typer.Typer(no_args_is_help=True)


@app.command()
def add(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Name or title of the expense.")],
    category: Annotated[
        str, typer.Argument(help="Category grouping (eg., Food, Transport).")
    ],
    expense: Annotated[
        float, typer.Argument(min=0.0, help="Monetary amount of the expense.")
    ],
    date: Annotated[
        datetime | None,
        typer.Option(
            "--date",
            "-d",
            help="Date of the expense. Accepted formats: YYYY-MM-DD or DD/MM/YYYY. Defaults to today.",
            formats=["%Y-%m-%d", "%d/%m/%Y"],
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description", "-desc", help="Optional detailed notes about the expense."
        ),
    ] = None,
) -> None:
    """Add a new expense to the database."""

    # Use today's date if no date is provided
    if date is None:
        target_date = datetime.now()
    else:
        target_date = date

    # Remove unnecessary spaces and capitalize the category
    fixed_category = category.strip().title()

    state: AppState = ctx.obj
    # Get the database and console
    db = state.expense
    console = state.console

    # Add the expense to the database
    row_id = db.add_expense(
        name=name,
        category=fixed_category,
        expense=expense,
        date=target_date,
        description=description,
    )

    # Check whether the expense was added
    if not row_id:
        console.print("[yellow]![/yellow] No expense was added.")
        raise typer.Exit()

    # Display success message
    console.print(
        f"[bold green]✓[/bold green] Expense of [cyan]{expense}[/cyan] "
        f"was successfully added for [cyan]{target_date.date()}[/cyan] "
        f"with ID [cyan]{row_id}[/cyan]"
    )


@app.command()
def list(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="Filter expense by a specific year.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
    month: Annotated[
        int | None,
        typer.Option(
            "--month",
            "-m",
            help="Filter expenses by month [1-12]. Requires --year",
            min=1,
            max=12,
            rich_help_panel="Date Arguments",
        ),
    ] = None,
) -> None:
    """Display all expenses with optional year and month filters."""

    # Check whether a month was provided without a year
    if month is not None and year is None:
        raise typer.BadParameter("Both --year and --month must be provided together.")

    state: AppState = ctx.obj

    # Get the database and console
    db = state.expense
    console = state.console

    # Get expenses from the database
    result = db.get_all_expenses(year=year, month=month)

    # Check whether any expenses were found
    if not result:
        console.print("i [dim]No expenses found in the database.[/dim]")
        raise typer.Exit()

    # Choose the table title
    if year is not None and month is not None:
        title = f"Expenses for [cyan]{year}/{month:02d}[/cyan]"

    elif year is not None:
        title = f"Expenses for year [cyan]{year}[/cyan]"

    else:
        title = "Expenses"

    # Create the Rich table
    table = Table(title=title, box=box.ROUNDED)

    # Add table columns
    table.add_column("ID", style="cyan", justify="left")
    table.add_column("Name", style="cyan", justify="left")
    table.add_column("Category", style="cyan", justify="left")
    table.add_column("Description", style="cyan", justify="left")
    table.add_column("Expense", style="green", justify="right")
    table.add_column("Date", style="cyan", justify="left")

    # Add expenses to the table
    for expense_data in result:
        expense_id = str(expense_data["id"])
        name = str(expense_data["name"])
        category = str(expense_data["category"])
        description = str(expense_data["description"])
        amount = str(expense_data["expense"])
        date = str(expense_data["date"])

        table.add_row(expense_id, name, category, description, amount, date)

    # Display the table
    console.print(table)


@app.command()
def list_by_id(
    ctx: typer.Context,
    expense_id: Annotated[
        int, typer.Argument(help="The unique ID of the expense to view.")
    ],
) -> None:
    """Display information about a particular expense."""

    state: AppState = ctx.obj

    # Get the database and console
    db = state.expense
    console = state.console

    # Get the expense using its ID
    result = db.get_expense(expense_id=expense_id)

    # Check whether the expense exists
    if result is None:
        console.print(
            f"[yellow]![/yellow] No expense found with ID [cyan]{expense_id}[/cyan]"
        )
        raise typer.Exit()

    # Create the Rich table
    table = Table(box=box.ROUNDED)

    # Add table columns
    table.add_column("ID", style="cyan", justify="left")
    table.add_column("Name", style="cyan", justify="left")
    table.add_column("Category", style="cyan", justify="left")
    table.add_column("Description", style="cyan", justify="left")
    table.add_column("Expense", style="green", justify="right")
    table.add_column("Date", style="cyan", justify="left")

    # Get the expense details
    expense_id_r = str(result["id"])
    name = str(result["name"])
    category = str(result["category"])
    description = str(result["description"])
    amount = str(result["expense"])
    date = str(result["date"])

    # Add the expense to the table
    table.add_row(expense_id_r, name, category, description, amount, date)

    # Display the table
    console.print(table)


@app.command()
def remove(
    ctx: typer.Context,
    expense_id: Annotated[
        int, typer.Argument(help="The unique ID of the expense to remove.", min=0)
    ],
) -> None:
    """Delete an expense from the database using its ID."""

    state: AppState = ctx.obj

    # Get the database and console
    db = state.expense
    console = state.console

    # Delete the expense
    result = db.delete_expense(expense_id=expense_id)

    # Check whether the expense was deleted
    if result is False:
        console.print(
            f"[yellow]![/yellow] No expense found to remove "
            f"for ID [cyan]{expense_id}[/cyan]"
        )
        raise typer.Exit()

    # Display success message
    console.print(
        f"[red]-[/red] Expense was successfully removed "
        f"for ID [cyan]{expense_id}[/cyan]"
    )


if __name__ == "__main__":
    app()
