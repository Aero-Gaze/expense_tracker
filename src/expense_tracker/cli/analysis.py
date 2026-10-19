from datetime import datetime
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from expense_tracker.analysis import ExpenseAnalytics

app = typer.Typer()


def _resolve_target_date(year: int | None, month: int | None) -> tuple[int, int]:
    """Validate that year and month are provided together, defaulting to today."""
    if (year is None) != (month is None):
        raise typer.BadParameter("Both --year and --month must be provided together.")

    target_year = year if year is not None else datetime.now().year
    target_month = month if month is not None else datetime.now().month

    return (target_year, target_month)


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
    """Lists category-wise spending with transaction counts.

    Optionally filter results by year and/or month.
    """

    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    console: Console = ctx.obj["console"]
    result = analysis.spending_by_category(year=year, month=month)
    if not result:
        console.print("[yellow]![/yellow] No expenses found to analyse.")
        raise typer.Exit()

    table = Table(title="Category Wise Spending", box=box.ROUNDED)

    # Format: (column_name, style, justify)
    columns = [
        ("Category", "cyan", "left"),
        ("Total Spent", "green", "right"),
        ("Count", "cyan", "right"),  # Internal column_name: transaction_count
    ]

    for column_name, style, justify in columns:
        table.add_column(column_name, style=style, justify=justify)

    for dict_row in result:
        rows = [str(row) for row in dict_row.values()]
        table.add_row(*rows)
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
    """Lists total monthly spending.

    Optionally filter results by year.
    """

    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    console: Console = ctx.obj["console"]
    result = analysis.monthly_spending(year=year)

    if not result:
        if not year:
            console.print("[yellow]![/yellow] No expenses to analyse.")
        else:
            console.print(
                f"[yellow]![/yellow] No expense to analyse for [cyan]{year}[/cyan]"
            )
        raise typer.Exit()

    table = Table(title="Month wise spending", box=box.ROUNDED)

    # Format: (column_name, style, justify)
    columns = [
        ("Year", "cyan", "center"),
        ("Month", "cyan", "center"),
        ("Total Spent", "green", "right"),
        ("Count", "cyan", "right"),
    ]

    for column_name, style, justify in columns:
        table.add_column(column_name, style=style, justify=justify)

    for dict_row in result:
        rows = [str(row) for row in dict_row.values()]
        table.add_row(*rows)

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
    """Displays the remaining budget for a specific month and year.

    Defaults to the current month and year if neither is provided. Both --year
    and --month must be specified together for filtering.
    """
    target_year, target_month = _resolve_target_date(year=year, month=month)

    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    console: Console = ctx.obj["console"]

    result = analysis.remaining_budget(year=target_year, month=target_month)
    if not result:
        console.print("[yellow]![/yellow] No budget was found.")
        raise typer.Exit()

    remaining_budget = result["remaining"]
    table = Table(
        title=f"Variance for [cyan]{target_year}/{target_month}[/cyan]", box=box.ROUNDED
    )
    if remaining_budget > 0:
        style = "green"
    elif remaining_budget == 0:
        style = "yellow"
    else:
        style = "red"

    table.add_column("Remaining Budget", style=style, justify="center")
    table.add_row(str(remaining_budget))

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
    """Check if spending exceeded the budget for a given period.

    Return True if over budget, otherwise False, or None if no budget is found.
    Defaults to the current month and year if neither is provided. Both --year
    and --month must be specified together if filtering manually.
    """

    target_year, target_month = _resolve_target_date(year=year, month=month)
    analysis: ExpenseAnalytics = ctx.obj["analysis"]

    result = analysis.is_over_budget(year=target_year, month=target_month)
    console: Console = ctx.obj["console"]

    if result is None:
        console.print("[yellow]![/yellow] No budget was found.")
        raise typer.Exit()

    table = Table(
        title=f"Over Budget for [cyan]{target_year}/{target_month}[/cyan]",
        box=box.ROUNDED,
    )
    if result:
        style = "red"
    else:
        style = "green"

    table.add_column("Over Budget ?", style=style, justify="center", width=20)
    table.add_row(str(result))

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
    """List average spending across all recorded months and years.

    Optionally filter results by year.
    """
    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    console: Console = ctx.obj["console"]
    result = analysis.average_expense(year=year)

    if year:
        title = f"Average Monthly Spending For [cyan]{year}[/cyan]"
    else:
        title = "Average Monthly Spending"

    if not result:
        console.print("[yellow]![/yellow] No average expense was found.")
        raise typer.Exit()

    table = Table(title=title, box=box.ROUNDED)
    table.add_column(
        "overall Average Spending", style="green", justify="center", width=30
    )
    table.add_row(str(result["overall_avg_monthly_spending"]))

    console.print(table)


# TODO: Fix summary display


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
    """Display overall financial summary."""
    if (year is None) != (month is None):
        raise typer.BadParameter("Both --year and --month must be provided together.")

    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    console: Console = ctx.obj["console"]

    result = analysis.summary(year=year, month=month)

    # if not result:
    #     console.print("[yellow]![/yellow] No summary was found.")
    #     raise typer.Exit()
    # table = Table(title="Summary", box=box.ROUNDED)
    # for column in result:
    #     table.add_column(str(column), style="cyan")
    #
    # rows = [str(row) for row in result.values()]
    # table.add_row(*rows)
    # console.print(table)


if __name__ == "__main__":
    app()
