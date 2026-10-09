import sqlite3
from pathlib import Path

# Base locations
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parents[2]  # Equivalent to .parent.parent.parent.parent


# Resource paths
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DB_DIR / "expenses.db"
SCHEMA_FILE = SRC_DIR / "schema.sql"


class Database:
    """
    A database layer to access the database.
    """

    def __init__(
        self, db_file: Path = DB_FILE, schema_file: Path = SCHEMA_FILE
    ) -> None:
        self.db_file: Path = db_file
        self.schema_file: Path = schema_file
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        query = self.schema_file.read_text(encoding="utf-8")
        with self.get_connection() as conn:
            conn.executescript(query)

    # ---------------
    # Expense Methods
    # ---------------
    def add_expense(
        self,
        name: str,
        category: str,
        expense: float,
        date: str,
        description: str | None = None,
    ) -> int | None:
        """Inserts an expense and return its ID."""

        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    """INSERT INTO expenses(name, category, description, expense, date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (name, category, description, expense, date),
                )

                expense_id = cursor.lastrowid

            return expense_id
        finally:
            conn.close()

    def get_expense(self, expense_id: int) -> dict | None:
        """Returns one expense or None if it doesn't exist."""

        conn = self.get_connection()
        try:
            with conn:
                row = conn.execute(
                    "SELECT * FROM expenses WHERE id = ?", (expense_id,)
                ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all_expense(self):
        """List all expenses."""
        conn = self.get_connection()
        try:
            with conn:
                rows = conn.execute("SELECT * FROM expenses").fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def delete_expense(self, expense_id: int) -> bool:
        """Deletes an expense by id. Returns False if not found"""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "DELETE FROM expenses WHERE id = ?", (expense_id,)
                )
            return cursor.rowcount > 0
        finally:
            conn.close()

    # --------------
    # Budget Methods
    # --------------

    def set_budget(self, year: int, month: int, amount: int):
        """Create or update a budget for the given month"""
        conn = self.get_connection()
        try:
            with conn:
                conn.execute(
                    """INSERT INTO budget (year, month, amount)
                    VALUES (?, ?, ?)
                    ON CONFLICT (year, month)
                    DO UPDATE SET amount = excluded.amount
                    """,
                    (year, month, amount),
                )
        finally:
            conn.close()

    def get_budget(self, year: int, month: int) -> dict | None:
        """Return a budget for a given year and month."""
        conn = self.get_connection()
        try:
            with conn:
                row = conn.execute(
                    """
                    SELECT *
                    FROM budget
                    WHERE year = ?
                    AND month = ?
                    """,
                    (year, month),
                ).fetchone()

            return dict(row) if row else None
        finally:
            conn.close()

    def get_all_budgets(self):
        """List all budgets, in chronological order."""
        conn = self.get_connection()
        try:
            with conn:
                rows = conn.execute(
                    "SELECT * FROM budget ORDER BY year, month"
                ).fetchall()
            return [dict(row) for row in rows]

        finally:
            conn.close()

    def delete_budget(self, year: int, month: int) -> bool:
        """Deletes a month's budget for a particular year. Return False if not found."""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute(
                    "DELETE FROM budget WHERE year = ? AND month = ?", (year, month)
                )
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_budget_by_id(self, budget_id: int):
        """Deletes a budget by id. Returns False if not found"""
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.execute("DELETE FROM budget WHERE id = ?", (budget_id,))
            return cursor.rowcount > 0
        finally:
            conn.close()
