from datetime import datetime
from os import getenv
from typing import Any

import pymysql
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Database connection details
DB_CONFIG = {
    "host": getenv("DB_HOST", "localhost"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "database": getenv("DB_NAME", "project_db"),
}


class DatabaseManager:
    """Handles the database connection and table creation."""

    def __init__(self) -> None:
        self._init_db()

    def get_connection(self) -> pymysql.Connection[pymysql.cursors.DictCursor]:
        """Creates and returns a database connection."""

        connection = pymysql.connect(
            **DB_CONFIG, cursorclass=pymysql.cursors.DictCursor
        )

        return connection

    def _init_db(self) -> None:
        """Creates the expenses and budgets tables if they do not exist."""

        # SQL query to create the expenses table
        create_expenses_table = """
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(255) NOT NULL,
                description TEXT,
                expense DECIMAL(10, 2) NOT NULL CHECK (expense >= 0),
                date DATE NOT NULL
            )
        """

        # SQL query to create the budgets table
        create_budgets_table = """
            CREATE TABLE IF NOT EXISTS budgets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT NOT NULL CHECK (year BETWEEN 1 AND 9999),
                month INT NOT NULL CHECK (month BETWEEN 1 AND 12),
                amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
                UNIQUE(year, month)
            )
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                # Create the expenses table
                cursor.execute(create_expenses_table)

                # Create the budgets table
                cursor.execute(create_budgets_table)

                # Save the changes
                connection.commit()

        finally:
            connection.close()


class ExpenseManager(DatabaseManager):
    """Handles all expense-related database operations."""

    def add_expense(
        self,
        name: str,
        category: str,
        expense: float,
        date: datetime,
        description: str | None = None,
    ) -> int | None:
        """Adds a new expense and returns its ID."""

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO expenses
                    (name, category, description, expense, date)
                    VALUES (%s, %s, %s, %s, %s)
                """

                values = (name, category, description, expense, date.date())

                cursor.execute(query, values)

                connection.commit()

                expense_id = cursor.lastrowid

                return expense_id

        finally:
            connection.close()

    def get_expense(self, expense_id: int) -> dict[str, Any] | None:
        """Returns one expense using its ID."""

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = "SELECT * FROM expenses WHERE id = %s"

                cursor.execute(query, (expense_id,))

                expense = cursor.fetchone()

                if expense is None:
                    return None

                return expense  # type: ignore

        finally:
            connection.close()

    def get_all_expenses(
        self, year: int | None = None, month: int | None = None
    ) -> list[dict[str, Any]] | None:
        """Returns all expenses, optionally filtered by year and month."""

        query = "SELECT * FROM expenses WHERE 1=1"

        params = []

        # Add year filter if a year is provided
        if year is not None:
            query += " AND YEAR(date) = %s"
            params.append(year)

        # Add month filter if a month is provided
        if month is not None:
            query += " AND MONTH(date) = %s"
            params.append(month)

        # Show newest expenses first
        query += " ORDER BY date DESC"

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)

                expenses = cursor.fetchall()

                if len(expenses) == 0:
                    return None

                return expenses  # type: ignore

        finally:
            connection.close()

    def delete_expense(self, expense_id: int) -> bool:
        """Deletes an expense and returns True if it was found."""

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = "DELETE FROM expenses WHERE id = %s"

                cursor.execute(query, (expense_id,))

                connection.commit()

                if cursor.rowcount > 0:
                    return True
                else:
                    return False

        finally:
            connection.close()


class BudgetManager(DatabaseManager):
    """Handles all budget-related database operations."""

    def set_budget(self, year: int, month: int, amount: float) -> bool:
        """Creates a new budget or updates an existing one."""

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO budgets (year, month, amount)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE amount = VALUES(amount)
                """

                values = (year, month, amount)

                cursor.execute(query, values)

                connection.commit()

                if cursor.rowcount > 0:
                    return True
                else:
                    return False

        finally:
            connection.close()

    def get_budgets(
        self, year: int | None = None, month: int | None = None
    ) -> list[dict[str, Any]] | None:
        """Returns all budgets, optionally filtered by year and month."""

        query = "SELECT * FROM budgets WHERE 1=1"

        params = []

        # Add year filter if provided
        if year is not None:
            query += " AND year = %s"
            params.append(year)

        # Add month filter if provided
        if month is not None:
            query += " AND month = %s"
            params.append(month)

        # Arrange budgets by year and month
        query += " ORDER BY year, month"

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)

                budgets = cursor.fetchall()

                if len(budgets) == 0:
                    return None

                return budgets  # type: ignore

        finally:
            connection.close()

    def delete_budget(self, year: int, month: int) -> bool:
        """Deletes a budget using its year and month."""

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = """
                    DELETE FROM budgets
                    WHERE year = %s AND month = %s
                """

                cursor.execute(query, (year, month))

                connection.commit()

                if cursor.rowcount > 0:
                    return True
                else:
                    return False

        finally:
            connection.close()

    def delete_budget_by_id(self, budget_id: int) -> bool:
        """Deletes a budget using its ID."""

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = "DELETE FROM budgets WHERE id = %s"

                cursor.execute(query, (budget_id,))

                connection.commit()

                if cursor.rowcount > 0:
                    return True
                else:
                    return False

        finally:
            connection.close()
