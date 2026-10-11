from datetime import datetime
from typing import Annotated

import typer

from expense_tracker.analysis.Analysis import ExpenseAnalytics

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
    result = analysis.spending_by_category(year=year, month=month)
    typer.echo(result)


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
    result = analysis.monthly_spending(year=year)
    typer.echo(result)


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

    result = analysis.remaining_budget(year=target_year, month=target_month)
    if not result:
        typer.echo("No budget found.")
        return
    typer.echo(result[2])


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
    typer.echo(result)


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
    result = analysis.average_expense(year=year)
    typer.echo(result)


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
    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.summary(year=year, month=month)

    typer.echo(result)


if __name__ == "__main__":
    app()
