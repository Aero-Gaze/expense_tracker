from re import A
from typing import Annotated
from warnings import resetwarnings

import typer

from expense_tracker.analysis.Analysis import ExpenseAnalytics

app = typer.Typer()


@app.command()
def category(ctx: typer.Context) -> None:
    """Lists category wise spending with transaction count."""

    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.spending_by_category()
    typer.echo(result)


@app.command()
def monthly(ctx: typer.Context) -> None:
    """Lists total monthly spending per year."""

    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.monthly_spending()
    typer.echo(result)


@app.command()
def variance(
    ctx: typer.Context,
    year: Annotated[int, typer.Option("--year", "-y", help="The year to analyse.")],
    month: Annotated[
        int, typer.Option("--month", "-m", help="The month to analyse.", min=1, max=12)
    ],
) -> None:
    """Lists the total budget remaining for a particular month and year."""
    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.remaining_budget(year=year, month=month)
    if not result:
        typer.echo("No budget found.")
        return
    typer.echo(result)


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
def average(ctx: typer.Context) -> None:
    """List the average spending for all months and years."""
    analysis: ExpenseAnalytics = ctx.obj["analysis"]
    result = analysis.average_expense()
    typer.echo(result[0])


if __name__ == "__main__":
    app()
