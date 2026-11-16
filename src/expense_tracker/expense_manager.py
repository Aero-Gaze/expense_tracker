from os import getenv

import pymysql
from dotenv import load_dotenv

# Load database settings
load_dotenv()

DB_CONFIG = {
    "host": getenv("DB_HOST", "localhost"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "database": getenv("DB_NAME", "project_db"),
}


class ExpenseManager:
    def __init__(self):
        self.create_tables()

    # ---------------- DATABASE ----------------

    def get_connection(self):
        return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

    def create_tables(self):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        category VARCHAR(255) NOT NULL,
                        description TEXT,
                        expense DECIMAL(10, 2) NOT NULL,
                        date DATE NOT NULL
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS budgets (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        year INT NOT NULL,
                        month INT NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        UNIQUE(year, month)
                    )
                """)

            connection.commit()

        finally:
            connection.close()

    # ---------------- EXPENSES ----------------

    def add_expense(self, name, category, expense, date, description=None):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO expenses
                    (name, category, expense, date, description)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        name,
                        category,
                        expense,
                        date.date() if hasattr(date, "date") else date,
                        description,
                    ),
                )

                connection.commit()
                return cursor.lastrowid

        finally:
            connection.close()

    def get_expense(self, expense_id):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM expenses WHERE id = %s", (expense_id,))
                return cursor.fetchone()

        finally:
            connection.close()

    def get_all_expenses(self, year=None, month=None):
        query = """
            SELECT * FROM expenses
            WHERE (%s IS NULL OR YEAR(date) = %s)
              AND (%s IS NULL OR MONTH(date) = %s)
            ORDER BY date DESC
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (year, year, month, month))
                return cursor.fetchall()

        finally:
            connection.close()

    def delete_expense(self, expense_id):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))

                connection.commit()
                return cursor.rowcount > 0

        finally:
            connection.close()

    # ---------------- BUDGETS ----------------

    def set_budget(self, year, month, amount):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO budgets (year, month, amount)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE amount = VALUES(amount)
                """,
                    (year, month, amount),
                )

                connection.commit()
                return cursor.rowcount > 0

        finally:
            connection.close()

    def get_budgets(self, year=None, month=None):
        query = """
            SELECT * FROM budgets
            WHERE (%s IS NULL OR year = %s)
              AND (%s IS NULL OR month = %s)
            ORDER BY year, month
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (year, year, month, month))
                return cursor.fetchall()

        finally:
            connection.close()

    def delete_budget(self, year, month):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM budgets
                    WHERE year = %s AND month = %s
                """,
                    (year, month),
                )

                connection.commit()
                return cursor.rowcount > 0

        finally:
            connection.close()

    def delete_budget_by_id(self, budget_id):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM budgets WHERE id = %s", (budget_id,))

                connection.commit()
                return cursor.rowcount > 0

        finally:
            connection.close()

    # ---------------- ANALYTICS ----------------

    # Get spending in each category
    def spending_by_category(self, year=None, month=None):
        query = """
            SELECT category,
                   SUM(expense) AS total_spent,
                   COUNT(*) AS transaction_count
            FROM expenses
            WHERE (%s IS NULL OR YEAR(date) = %s)
              AND (%s IS NULL OR MONTH(date) = %s)
            GROUP BY category
            ORDER BY total_spent DESC
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (year, year, month, month))
                return cursor.fetchall()

        finally:
            connection.close()

    # Get spending for each month
    def monthly_spending(self, year=None):
        query = """
            SELECT YEAR(date) AS year,
                   MONTH(date) AS month,
                   SUM(expense) AS total_spent,
                   COUNT(*) AS transaction_count
            FROM expenses
            WHERE (%s IS NULL OR YEAR(date) = %s)
            GROUP BY YEAR(date), MONTH(date)
            ORDER BY year DESC, month
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (year, year))
                return cursor.fetchall()

        finally:
            connection.close()

    # Calculate remaining budget
    def remaining_budget(self, year, month):
        query = """
            SELECT budgets.amount AS total_budget,
                   COALESCE(SUM(expenses.expense), 0) AS total_spent
            FROM budgets
            LEFT JOIN expenses
              ON YEAR(expenses.date) = budgets.year
             AND MONTH(expenses.date) = budgets.month
            WHERE budgets.year = %s AND budgets.month = %s
            GROUP BY budgets.amount
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (year, month))
                result = cursor.fetchone()

        finally:
            connection.close()

        if result is None:
            return None

        budget = result["total_budget"]
        spent = result["total_spent"]

        return {
            "total_budget": budget,
            "total_spent": spent,
            "remaining": budget - spent,
        }

    # Check if spending is over budget
    def is_over_budget(self, year, month):
        budget = self.remaining_budget(year, month)

        if budget is None:
            return None

        return budget["remaining"] < 0

    # Calculate average monthly spending
    def average_expense(self, year=None):
        query = """
            SELECT AVG(monthly_total) AS average_spending
            FROM (
                SELECT SUM(expense) AS monthly_total
                FROM expenses
                WHERE (%s IS NULL OR YEAR(date) = %s)
                GROUP BY YEAR(date), MONTH(date)
            ) AS monthly_expenses
        """

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (year, year))
                result = cursor.fetchone()
                return result["average_spending"] if result else None

        finally:
            connection.close()

    # Get complete expense summary
    def summary(self, year=None, month=None):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT SUM(expense) AS total_spent,
                           COUNT(*) AS total_transactions
                    FROM expenses
                """)

                result = cursor.fetchone()

        finally:
            connection.close()

        categories = self.spending_by_category(year, month)

        summary = {
            "total_spent_all_time": float(result["total_spent"] or 0),
            "total_transactions": result["total_transactions"],
            "overall_avg_monthly_spending": self.average_expense(year) or 0,
            "top_spending_category": categories[0]["category"] if categories else None,
        }

        # Add monthly information if both values are provided
        if year is None or month is None:
            return summary

        budget = self.remaining_budget(year, month)

        if budget:
            monthly_spent = budget["total_spent"]
            monthly_budget = budget["total_budget"]
            remaining = budget["remaining"]
            over_budget = remaining < 0

        else:
            monthly_budget = None
            remaining = None
            over_budget = None

            months = self.monthly_spending(year)

            monthly_spent = next(
                (item["total_spent"] for item in months if item["month"] == month), 0
            )

        summary.update(
            {
                "monthly_spent": monthly_spent,
                "monthly_budget": monthly_budget,
                "remaining_budget": remaining,
                "is_over_budget": over_budget,
            }
        )

        return summary
