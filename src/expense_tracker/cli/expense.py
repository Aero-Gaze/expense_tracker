from datetime import datetime
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from expense_tracker.database import ExpenseManager

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
            "--description", "-desc", help="optional detailed notes about the expense."
        ),
    ] = None,
) -> None:
    """Add a new expense record to database.

    Saves the expense name, category, amount, optional date and description.
    If no date is provided, the current system date is used automatically.
    """
    target_date = date if date is not None else datetime.now()
    fixed_category = category.strip().title()

    db: ExpenseManager = ctx.obj["expense"]
    console: Console = ctx.obj["console"]

    row_id = db.add_expense(
        name=name,
        category=fixed_category,
        expense=expense,
        date=target_date,
        description=description,
    )
    if not row_id:
        console.print("[yellow]![/yellow] No expense was added.")
        raise typer.Exit()
    console.print(
        f"[bold green]✓[/bold green] Expense of [cyan]{expense}[/cyan] was successfully added for [cyan]{target_date.date()}[/cyan] with ID [cyan]{row_id}[/cyan]"
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
    """List all recorded expenses with optional year and month filters.

    To filter by month, you must also specify the year using the --year option.
    """
    if month and (not year):
        raise typer.BadParameter("Both --year and --month must be provided together.")

    db: ExpenseManager = ctx.obj["expense"]
    console: Console = ctx.obj["console"]

    result = db.get_all_expenses(year=year, month=month)

    if not result:
        console.print("i [dim]No expenses found in the database.[/dim]")
        raise typer.Exit()

    if year and month:
        title = f"Expenses for [cyan]{year}/{month:02d}[/cyan]"
    elif year:
        title = f"Expenses for year [cyan]{year}[/cyan]"
    else:
        title = "Expenses"

    table = Table(title=title, box=box.ROUNDED)

    # Format: (column_name, style, justify)
    columns = [
        ("ID", "cyan", "left"),
        ("Name", "cyan", "left"),
        ("Category", "cyan", "left"),
        ("Description", "cyan", "left"),
        ("Expense", "green", "right"),
        ("Date", "cyan", "left"),
    ]

    for column_name, style, justify in columns:
        table.add_column(column_name, style=style, justify=justify)  # type: ignore

    for dict_row in result:
        rows = [str(val) for val in dict_row.values()]
        table.add_row(*rows)

    console.print(table)


@app.command()
def list_by_id(
    ctx: typer.Context,
    expense_id: Annotated[
        int, typer.Argument(help="The unique ID of the expense to view.")
    ],
):
    """ "Display detailed information for a single expense by its unique ID."""
    db: ExpenseManager = ctx.obj["expense"]
    console: Console = ctx.obj["console"]
    result = db.get_expense(expense_id=expense_id)

    if not result:
        console.print(
            f"[yellow]![/yellow] No expense found with ID [cyan]{expense_id}[/cyan]"
        )
        raise typer.Exit()

    table = Table(box=box.ROUNDED)

    # Format: (column_name, style, justify)
    columns = [
        ("ID", "cyan", "left"),
        ("Name", "cyan", "left"),
        ("Category", "cyan", "left"),
        ("Description", "cyan", "left"),
        ("Expense", "green", "right"),
        ("Date", "cyan", "left"),
    ]
    for column_name, style, justify in columns:
        table.add_column(column_name, style=style, justify=justify)  # type: ignore

    rows = [str(val) for val in result.values()]
    table.add_row(*rows)

    console.print(table)


@app.command()
def remove(
    ctx: typer.Context,
    expense_id: Annotated[
        int, typer.Argument(help="The unique ID of the expense to remove.", min=0)
    ],
) -> None:
    """Permanently delete an expense record from the database by its ID."""
    db: ExpenseManager = ctx.obj["expense"]
    console: Console = ctx.obj["console"]

    result = db.delete_expense(expense_id=expense_id)

    if not result:
        console.print(
            f"[yellow]![/yellow] No expense found to remove for ID [cyan]{expense_id}[/cyan]"
        )
        raise typer.Exit()
    console.print(
        f"[red]-[/red] Expense was successfully removed for ID [cyan]{expense_id}[/cyan]"
    )


if __name__ == "__main__":
    app()
