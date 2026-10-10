from typing import Annotated

import typer

from expense_tracker.analysis.Analysis import ExpenseAnalytics

app = typer.Typer()


@app.command()
def category(
    ctx: typer.Context,
    year: Annotated[int | None, typer.Option("--year", "-y", help="The year to categorise.")] = None,
    month: Annotated[int | None, typer.Option("--month", "-m", help="The month to categorise.")] = None
) -> None:
    """Lists category wise spending with transaction count, optionally filtered by year and/or month."""

    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.spending_by_category(year=year, month=month)
    typer.echo(result)


@app.command()
def monthly(
    ctx: typer.Context,
    year: Annotated[int | None, typer.Option("--year", "-y", help="The year to search.")] = None
) -> None:
    """Lists total monthly spending per year, optionally filtered by year."""

    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.monthly_spending(year=year)
    typer.echo(result)


@app.command()
def variance(
    ctx: typer.Context,
    year: Annotated[int, typer.Option("--year", "-y", help="The year to analyse.")],
    month: Annotated[
        int, typer.Option("--month", "-m", help="The month to analyse.", min=1, max=12)
    ],
) -> None:
    """Displays the total budget remaining for a particular month and year."""
    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.remaining_budget(year=year, month=month)
    if not result:
        typer.echo("No budget found.")
        return
    typer.echo(result[2])


@app.command()
def over_budget(
    ctx: typer.Context,
    year: Annotated[int, typer.Option("--year", "-y", help="The year to analyse.")],
    month: Annotated[
        int, typer.Option("--month", "-m", help="The month to analyse.", min=1, max=12)
    ],
) -> None:
    """Lists True or False if over budget, or None if no budget is found."""
    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.is_over_budget(year=year, month=month)
    typer.echo(result)


@app.command()
def average(
    ctx: typer.Context, year: Annotated[int | None, typer.Option("--year", "-y", help="The year to search.")] = None
) -> None:
    """List the average spending for all months and years."""
    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.average_expense(year=year)
    typer.echo(result)


@app.command()
def summary(
    ctx: typer.Context,
    year: Annotated[
        int | None, typer.Option("--year", "-y", help="The year to summarize.")
    ] = None,
    month: Annotated[
        int | None, typer.Option("--month", "-m", help="The month to summarize.")
    ] = None,
) -> None:
    """Overall financial summary."""
    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.summary(year=year, month=month)

    typer.echo(result)


if __name__ == "__main__":
    app()
