from datetime import datetime
from typing import Annotated

import typer
from rich import box
from rich.panel import Panel
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

    # Get the current date
    today = datetime.now()

    # Use the current year if no year is provided
    if year is None:
        target_year = today.year
    else:
        target_year = year

    # Use the current month if no month is provided
    if month is None:
        target_month = today.month
    else:
        target_month = month

    return target_year, target_month


@app.command()
def category(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="Filter spending by specific year.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
    month: Annotated[
        int | None,
        typer.Option(
            "--month",
            "-m",
            help="Filter spending by specific month [1-12].",
            rich_help_panel="Date Arguments",
            min=1,
            max=12,
        ),
    ] = None,
) -> None:
    """Display spending for each category."""

    state: AppState = ctx.obj

    # Get the analysis object and console
    analysis = state.analysis
    console = state.console

    # Get category-wise spending
    result = analysis.spending_by_category(year=year, month=month)

    # Check whether any expenses were found
    if not result:
        console.print("[yellow]![/yellow] No expenses found to analyse.")
        raise typer.Exit()

    # Create a Rich table
    table = Table(title="Category Wise Spending", box=box.ROUNDED)

    # Add table columns
    table.add_column("Category", style="cyan", justify="left")
    table.add_column("Total Spent", style="green", justify="right")
    table.add_column("Count", style="cyan", justify="right")

    # Add category information to the table
    for category_data in result:
        category_name = str(category_data["category"])
        total_spent = str(category_data["total_spent"])
        transaction_count = str(category_data["transaction_count"])

        table.add_row(category_name, total_spent, transaction_count)

    # Display the table
    console.print(table)


@app.command()
def monthly(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="Filter monthly spending by specific year.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
) -> None:
    """Display total spending for each month."""

    state: AppState = ctx.obj

    # Get the analysis object and console
    analysis = state.analysis
    console = state.console

    # Get monthly spending
    result = analysis.monthly_spending(year=year)

    # Check whether any expenses were found
    if not result:
        if year is None:
            console.print("[yellow]![/yellow] No expenses to analyse.")
        else:
            console.print(
                f"[yellow]![/yellow] No expense to analyse for [cyan]{year}[/cyan]"
            )

        raise typer.Exit()

    # Create a Rich table
    table = Table(title="Month wise spending", box=box.ROUNDED)

    # Add table columns
    table.add_column("Year", style="cyan", justify="center")
    table.add_column("Month", style="cyan", justify="center")
    table.add_column("Total Spent", style="green", justify="right")
    table.add_column("Count", style="cyan", justify="right")

    # Add monthly spending information
    for month_data in result:
        spending_year = str(month_data["year"])
        spending_month = str(month_data["month"])
        total_spent = str(month_data["total_spent"])
        transaction_count = str(month_data["transaction_count"])

        table.add_row(spending_year, spending_month, total_spent, transaction_count)

    # Display the table
    console.print(table)


@app.command()
def variance(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="The year to analyse.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
    month: Annotated[
        int | None,
        typer.Option(
            "--month",
            "-m",
            help="The month to analyse [1-12].",
            rich_help_panel="Date Arguments",
            min=1,
            max=12,
        ),
    ] = None,
) -> None:
    """Display the remaining budget for a particular month."""

    # Get the year and month
    target_year, target_month = _resolve_target_date(year, month)

    state: AppState = ctx.obj

    # Get the analysis object and console
    analysis = state.analysis
    console = state.console

    # Get the remaining budget
    result = analysis.remaining_budget(year=target_year, month=target_month)

    # Check whether a budget exists
    if result is None:
        console.print("[yellow]![/yellow] No budget was found.")
        raise typer.Exit()

    # Get the remaining amount
    remaining_budget = result["remaining"]

    # Create the table
    table = Table(
        title=f"Variance for [cyan]{target_year}/{target_month}[/cyan]", box=box.ROUNDED
    )

    # Choose a colour based on the remaining budget
    if remaining_budget > 0:
        style = "green"

    elif remaining_budget == 0:
        style = "yellow"

    else:
        style = "red"

    # Add the remaining budget to the table
    table.add_column("Remaining Budget", style=style, justify="center")

    table.add_row(str(remaining_budget))

    # Display the table
    console.print(table)


@app.command()
def over_budget(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="The year to analyse.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
    month: Annotated[
        int | None,
        typer.Option(
            "--month",
            "-m",
            help="The month to analyse [1-12].",
            rich_help_panel="Date Arguments",
            min=1,
            max=12,
        ),
    ] = None,
) -> None:
    """Check whether spending exceeded the budget."""

    # Get the year and month
    target_year, target_month = _resolve_target_date(year, month)

    state: AppState = ctx.obj

    # Get the analysis object and console
    analysis = state.analysis
    console = state.console

    # Check whether the spending is over budget
    result = analysis.is_over_budget(year=target_year, month=target_month)

    # Check whether a budget exists
    if result is None:
        console.print("[yellow]![/yellow] No budget was found.")
        raise typer.Exit()

    # Create the table
    table = Table(
        title=f"Over Budget for [cyan]{target_year}/{target_month}[/cyan]",
        box=box.ROUNDED,
    )

    # Choose a colour based on the result
    if result is True:
        style = "red"
    else:
        style = "green"

    # Add the result to the table
    table.add_column("Over Budget ?", style=style, justify="center", width=20)

    table.add_row(str(result))

    # Display the table
    console.print(table)


@app.command()
def average(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="Filter average spending by a specific year.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
) -> None:
    """Display average monthly spending."""

    state: AppState = ctx.obj

    # Get the analysis object and console
    analysis = state.analysis
    console = state.console

    # Get average monthly spending
    result = analysis.average_expense(year=year)

    # Choose the table title
    if year:
        title = f"Average Monthly Spending for Year [cyan]{year}[/cyan]"
    else:
        title = "Average Monthly Spending"

    # Check whether an average was found
    if not result:
        console.print("[yellow]![/yellow] No average expense was found.")
        raise typer.Exit()

    # Create the table
    table = Table(title=title, box=box.ROUNDED)

    table.add_column(
        "overall Average Spending", style="green", justify="center", width=30
    )

    table.add_row(str(result))

    # Display the table
    console.print(table)


@app.command()
def summary(
    ctx: typer.Context,
    year: Annotated[
        int | None,
        typer.Option(
            "--year",
            "-y",
            help="Filter summary by a specific year.",
            rich_help_panel="Date Arguments",
        ),
    ] = None,
    month: Annotated[
        int | None,
        typer.Option(
            "--month",
            "-m",
            help="Filter summary by a specific month [1-12].",
            rich_help_panel="Date Arguments",
            min=1,
            max=12,
        ),
    ] = None,
) -> None:
    """Display the overall financial summary."""

    # Check whether both year and month are provided
    if year is None and month is not None:
        raise typer.BadParameter("Both --year and --month must be provided together.")

    if month is None and year is not None:
        raise typer.BadParameter("Both --year and --month must be provided together.")

    state: AppState = ctx.obj

    # Get the analysis object and console
    analysis = state.analysis
    console = state.console

    # Get the financial summary
    result = analysis.summary(year=year, month=month)

    # Check whether a summary was found
    if result is None:
        console.print("[yellow]![/yellow] No summary was found.")
        raise typer.Exit()

    # Convert the summary information into readable text
    content = ""

    for key, value in result.items():
        # Replace underscores with spaces
        readable_key = key.replace("_", " ")

        # Capitalize the words
        readable_key = readable_key.title()

        # Add the information to the content
        content += f"[bold cyan]{readable_key}: [/bold cyan]{value}\n"

    # Choose the panel title
    if year is not None and month is not None:
        title = f"[bold]Expense Summary[/bold] for [cyan]{year}/{month}[/cyan]"
    else:
        title = "[bold]Expense Summary[/bold]"

    # Create the Rich panel
    panel = Panel(content, title=title)

    # Display the panel
    console.print(panel)


if __name__ == "__main__":
    app()
