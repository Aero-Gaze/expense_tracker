
from decimal import Decimal
from typing import Any

from expense_tracker.database import DatabaseManager


class ExpenseAnalytics:
    """Handles data analysis for expenses and budgets."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def spending_by_category(
        self, year: int | None = None, month: int | None = None
    ) -> list[dict[str, Any]]:
        """Returns spending and transaction count for each category."""

        query = """
            SELECT
                category,
                SUM(expense) AS total_spent,
                COUNT(expense) AS transaction_count
            FROM expenses
            WHERE 1=1
        """

        params = []

        # Add year filter if a year is provided
        if year is not None:
            query += " AND YEAR(date) = %s"
            params.append(year)

        # Add month filter if a month is provided
        if month is not None:
            query += " AND MONTH(date) = %s"
            params.append(month)

        query += " GROUP BY category ORDER BY total_spent DESC"

        conn = self.db.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result  # type: ignore
        finally:
            conn.close()

    def monthly_spending(self, year: int | None = None) -> list[dict[str, Any]]:
        """Returns total spending for each month."""

        query = """
            SELECT
                YEAR(date) AS year,
                MONTH(date) AS month,
                SUM(expense) AS total_spent,
                COUNT(expense) AS transaction_count
            FROM expenses
            WHERE 1=1
        """

        params = []

        # Filter by year if provided
        if year is not None:
            query += " AND YEAR(date) = %s"
            params.append(year)

        query += " GROUP BY year, month ORDER BY year DESC, month"

        conn = self.db.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result  # type: ignore
        finally:
            conn.close()

    def remaining_budget(self, year: int, month: int) -> dict[str, Decimal] | None:
        """Returns the budget, spending and remaining money."""

        query = """
            SELECT
                B.amount AS total_budget,
                COALESCE(SUM(E.expense), 0) AS total_spent
            FROM budgets AS B
            LEFT JOIN expenses AS E
                ON YEAR(E.date) = B.year
                AND MONTH(E.date) = B.month
            WHERE B.year = %s AND B.month = %s
            GROUP BY B.amount
        """

        conn = self.db.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (year, month))
                result = cursor.fetchone()
        finally:
            conn.close()

        # No budget was found
        if result is None:
            return None

        total_budget = result["total_budget"]
        total_spent = result["total_spent"]

        remaining = total_budget - total_spent

        return {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": remaining
        }

    def is_over_budget(self, year: int, month: int) -> bool | None:
        """Checks whether spending is greater than the budget."""

        budget = self.remaining_budget(year, month)

        if budget is None:
            return None

        remaining = budget["remaining"]

        if remaining < 0:
            return True
        else:
            return False

    def average_expense(self, year: int | None = None) -> Decimal | None:
        """Returns the average monthly spending."""

        query = """
            SELECT AVG(total_spent) AS average_monthly_spending
            FROM (
                SELECT SUM(expense) AS total_spent
                FROM expenses
                WHERE 1=1
        """

        params = []

        # Filter by year if provided
        if year is not None:
            query += " AND YEAR(date) = %s"
            params.append(year)

        query += """
                GROUP BY YEAR(date), MONTH(date)
            ) AS monthly_total
        """

        conn = self.db.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()

                if result is None:
                    return None

                return result["average_monthly_spending"]

        finally:
            conn.close()

    def summary(
        self, year: int | None = None, month: int | None = None
    ) -> dict[str, Any] | None:
        """Returns a complete summary of expenses."""

        # Get total spending and transaction count
        query = """
            SELECT
                SUM(expense) AS total_spent,
                COUNT(*) AS total_transactions
            FROM expenses
        """

        conn = self.db.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                overall = cursor.fetchone()

        finally:
            conn.close()

        # Return None if no result was found
        if overall is None:
            return None

        total_spent = float(overall["total_spent"] or Decimal(0))
        total_transactions = int(overall["total_transactions"] or Decimal(0))

        # Get average monthly spending
        average_spending = self.average_expense(year)

        if average_spending is None:
            average_spending = 0.0

        # Get spending by category
        categories = self.spending_by_category(year, month)

        # Find the category with the highest spending
        if len(categories) > 0:
            top_category = categories[0]["category"]
        else:
            top_category = None

        # Create the main summary
        summary_data = {
            "total_spent_all_time": total_spent,
            "total_transactions": total_transactions,
            "overall_avg_monthly_spending": average_spending,
            "top_spending_category": top_category
        }

        # Add monthly budget details only if both year and month are provided
        if year is None or month is None:
            return summary_data

        # Get the budget for the selected month
        budget_data = self.remaining_budget(year, month)

        if budget_data is not None:

            monthly_budget = budget_data["total_budget"]
            monthly_spent = budget_data["total_spent"]
            remaining = budget_data["remaining"]

            if remaining < 0:
                is_over = True
            else:
                is_over = False

        else:
            # No budget exists for this month
            monthly_budget = None
            remaining = None
            is_over = None

            # Find how much was spent during this month
            months = self.monthly_spending(year)

            monthly_spent = 0.0

            for month_data in months:
                if month_data["month"] == month:
                    monthly_spent = month_data["total_spent"]
                    break

        # Add monthly information to the summary
        summary_data["monthly_spent"] = monthly_spent
        summary_data["monthly_budget"] = monthly_budget
        summary_data["remaining_budget"] = remaining
        summary_data["is_over_budget"] = is_over

        return summary_data
