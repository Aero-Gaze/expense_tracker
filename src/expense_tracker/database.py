from datetime import datetime
from os import getenv

import mariadb
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": getenv("DB_HOST", "localhost"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "database": getenv("DB_NAME", "project_db"),
}


class DatabaseManager:
    """
    A database layer to access the database.
    """

    def __init__(self, db_config: dict[str, str] = DB_CONFIG) -> None:
        self.db_config: dict[str, str] = db_config
        self._init_db()

    def get_connection(self) -> mariadb.Connection:
        return mariadb.connect(**self.db_config)

    def _init_db(self) -> None:
        create_queries: list[str] = [
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(255) NOT NULL,
                description TEXT,
                expense DECIMAL(10, 2) NOT NULL CHECK (expense >= 0),
                date DATE NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT NOT NULL CHECK (year BETWEEN 1 AND 9999),
                month INT NOT NULL CHECK (month BETWEEN 1 and 12),
                amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),

                UNIQUE(year, month)
            )
            """,
        ]
        with self.get_connection() as conn, conn.cursor() as cursor:
            for query in create_queries:
                cursor.execute(query)
            conn.commit()

    # ---------------
    # Expense Methods
    # ---------------
    def add_expense(
        self,
        name: str,
        category: str,
        expense: float,
        date: datetime,
        description: str | None = None,
    ) -> int | None:
        """Inserts an expense and return its ID."""
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO expenses(name, category, description, expense, date) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, category, description, expense, date.date()),
            )
            conn.commit()
            return cursor.lastrowid

    def get_expense(self, expense_id: int) -> dict | None:
        """Returns one expense or None if it doesn't exist."""

        with self.get_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT * FROM expenses WHERE id = %s
                """,
                (expense_id,),
            )
            row = cursor.fetchone()
            return row if row else None

    def get_all_expenses(
        self, year: int | None = None, month: int | None = None
    ) -> list[dict] | None:
        """List all expenses, takes year and month as parameter(optional)."""
        query = ["SELECT * FROM expenses WHERE 1=1"]
        params = []

        if year is not None:
            query.append("AND YEAR(date) = %s")
            params.append(year)
        if month is not None:
            query.append("AND MONTH(date) = %s")
            params.append(month)

        query.append("ORDER BY date DESC")

        with self.get_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(" ".join(query), params)
            rows = cursor.fetchall()
            return rows if rows else None

    def delete_expense(self, expense_id: int) -> bool:
        """Deletes an expense by id. Returns False if not found"""
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM expenses WHERE id = %s
                """,
                (expense_id,),
            )
            row_count = cursor.rowcount
            conn.commit()
            return row_count > 0

    # --------------
    # Budget Methods
    # --------------

    def set_budget(self, year: int, month: int, amount: float) -> bool:
        """Create or update a budget for the given month"""
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO budgets(year, month, amount)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE amount = VALUES(amount)
                """,
                (year, month, amount),
            )
            row_count = cursor.rowcount
            conn.commit()
            return row_count > 0

    def get_budgets(
        self, year: int | None = None, month: int | None = None
    ) -> list[dict] | None:
        """List all budgets, in chronological order with optional filtering."""
        query = ["SELECT * FROM budgets WHERE 1=1"]
        params = []

        if year is not None:
            query.append("AND year = %s")
            params.append(year)
        if month is not None:
            query.append("AND month = %s")
            params.append(month)

        query.append("ORDER BY year, month")

        with self.get_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(" ".join(query), params)
            rows = cursor.fetchall()
            return rows if rows else None

    def delete_budget(self, year: int, month: int) -> bool:
        """Deletes a month's budget for a particular year. Return False if not found."""
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM budgets WHERE year = %s AND month = %s
                """,
                (year, month),
            )
            row_count = cursor.rowcount
            conn.commit()
            return row_count > 0

    def delete_budget_by_id(self, budget_id: int):
        """Deletes a budget by id. Returns False if not found"""
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM budgets WHERE id = %s
                """,
                (budget_id,),
            )
            row_count = cursor.rowcount
            conn.commit()
            return row_count > 0
