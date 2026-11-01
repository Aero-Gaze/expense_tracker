from dataclasses import dataclass, field

from rich.console import Console

from expense_tracker.analysis import ExpenseAnalytics
from expense_tracker.database import BudgetManager, DatabaseManager, ExpenseManager


@dataclass
class AppState:
    db: DatabaseManager = field(default_factory=DatabaseManager)
    analysis: ExpenseAnalytics = field(init=False)
    expense: ExpenseManager = field(default_factory=ExpenseManager)
    budget: BudgetManager = field(default_factory=BudgetManager)
    console: Console = field(default_factory=Console)

    def __post_init__(self):
        self.analysis = ExpenseAnalytics(self.db)
