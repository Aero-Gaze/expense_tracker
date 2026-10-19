import typer
from rich.console import Console

from expense_tracker.analysis import ExpenseAnalytics
from expense_tracker.cli.analysis import app as analysis_app
from expense_tracker.cli.budget import app as budget_app
from expense_tracker.cli.expense import app as expense_app
from expense_tracker.database import DatabaseManager

app = typer.Typer(
    name="expense-tracker",
    help="A simple expense tracker using python",
    add_completion=False,
)

app.add_typer(budget_app, name="budget", help="All commands related to budget.")
app.add_typer(expense_app, name="expense", help="All commands related to expense.")
app.add_typer(analysis_app, name="analysis", help="All commands related to analysis.")


@app.callback()
def main(
    ctx: typer.Context,
):
    ctx.ensure_object(dict)
    ctx.obj["db"] = DatabaseManager()
    ctx.obj["analysis"] = ExpenseAnalytics(ctx.obj["db"])
    ctx.obj["console"] = Console()


if __name__ == "__main__":
    app()
