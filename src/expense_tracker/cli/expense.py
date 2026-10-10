from datetime import datetime
from typing import Annotated

import typer

from expense_tracker.database.Database import DatabaseManager

app = typer.Typer()


@app.command()
def add(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Name of the expense.")],
    category: Annotated[str, typer.Argument(help="Category of the expense.")],
    expense: Annotated[float, typer.Argument(min=0.0)],
    date: Annotated[
        str | None,
        typer.Argument(help="Date of the expense (defaults to todays date)."),
    ] = None,
    description: Annotated[
        str | None, typer.Argument(help="Description of the expense.")
    ] = None,
) -> None:
    """Add an expense. Date defaults to today's date if not given and description is optional."""
    target_date = date if date is not None else str(datetime.date(datetime.now()))

    db: DatabaseManager = ctx.obj["db"]

    row_id = db.add_expense(
        name=name,
        category=category.title(),
        expense=expense,
        date=target_date,
        description=description,
    )

    if not row_id:
        typer.echo("Expense not added.")
        return
    typer.echo(f"Expense of {expense} added for {target_date}")


@app.command()
def list(
    ctx: typer.Context,
    year: Annotated[
        int | None, typer.Option("--year", "-y", help="The year of the expense.")
    ] = None,
    month: Annotated[
        int | None,
        typer.Option("--month", "-m", help="The month of the expense.", min=1, max=12),
    ] = None,
) -> None:
    """List all expenses (optionally filtered by year and month)"""
    db: DatabaseManager = ctx.obj["db"]

    result = db.get_all_expenses(year=year, month=month)
    if not result:
        typer.echo("No expenses found.")
        return
    typer.echo(result)


@app.command()
def list_by_id(
    ctx: typer.Context,
    expense_id: Annotated[int, typer.Argument(help="The Id of the expense.")],
):
    """List the expense by Id."""
    db: DatabaseManager = ctx.obj["db"]
    result = db.get_expense(expense_id=expense_id)

    if not result:
        typer.echo("No expense found.")
        return
    typer.echo(result)


@app.command()
def remove(
    ctx: typer.Context,
    expense_id: Annotated[int, typer.Argument(help="The Id of the expense.", min=0)],
) -> None:
    """Remove the specified expense by id."""
    db: DatabaseManager = ctx.obj["db"]
    result = db.delete_expense(expense_id=expense_id)
    if not result:
        typer.echo("No expenses deleted.")
        return
    typer.echo(f"Deleted expense: {expense_id}")


if __name__ == "__main__":
    app()
