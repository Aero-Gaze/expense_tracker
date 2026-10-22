from decimal import Decimal

from expense_tracker.database import DatabaseManager


class ExpenseAnalytics:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def spending_by_category(
        self, year: int | None = None, month: int | None = None
    ) -> list[dict]:
        """Returns category wise spending and count, optionally filtered by year and/or month."""
        query = [
            """
            SELECT category,
                SUM(expense) as total_spent,
                COUNT(expense) as transaction_count
            FROM expenses WHERE 1=1
            """
        ]
        params = []

        if year is not None:
            query.append("AND YEAR(date) = %s")
            params.append(year)
        if month is not None:
            query.append("AND MONTH(date) = %s")
            params.append(month)

        query.append("GROUP BY category ORDER BY total_spent DESC")

        with self.db.get_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(" ".join(query), tuple(params))
            return cursor.fetchall()

    def monthly_spending(self, year: int | None = None) -> list[dict]:
        """Returns total monthly spending per year, optionally filtered by year."""
        query = [
            """
            SELECT
                YEAR(date) AS year,
                MONTH(date) AS month,
                SUM(expense) as total_spent,
            COUNT(expense) as transaction_count
            FROM expenses WHERE 1=1
            """
        ]
        params = []

        if year is not None:
            query.append("AND YEAR(date) = %s")
            params.append(year)

        query.append("GROUP BY year, month ORDER BY year DESC, month")

        with self.db.get_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(" ".join(query), tuple(params))
            return cursor.fetchall()

    def remaining_budget(self, year: int, month: int) -> dict[str, Decimal] | None:
        """Returns (total_budget, total_spent, total_budget - total_spent), or None if no budget exists."""
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

        with self.db.get_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(query, (year, month))
            result = cursor.fetchone()

        if result is None:
            return None

        total_budget = result["total_budget"]
        total_spent = result["total_spent"]

        return {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": total_budget - total_spent,
        }

    def is_over_budget(self, year: int, month: int) -> bool | None:
        """Returns True if over budget, or None if budget does not exist."""
        budget = self.remaining_budget(year=year, month=month)
        if budget is None:
            return None
        return budget["remaining"] < 0

    def average_expense(self, year: int | None = None) -> Decimal | None:
        """Returns the average expense for a particular or all the years."""

        query = [
            """
            SELECT AVG(total_spent) AS average_monthly_spending
            FROM (
                SELECT
                    SUM(expense) AS total_spent
                FROM expenses
                WHERE 1=1
            """
        ]
        params = []

        if year is not None:
            query.append("AND YEAR(DATE) = %s")
            params.append(year)
        query.append(
            """
                GROUP BY YEAR(DATE), MONTH(DATE)
            ) AS monthly_total
            """
        )

        with self.db.get_connection() as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(" ".join(query), params)
            result = cursor.fetchone()
            return result["average_monthly_spending"] if result else None

    def summary(self, year: int | None = None, month: int | None = None) -> dict:
        """Returns a comprehensive financial summary."""

        with self.db.get_connection() as conn, conn.cursor(dictionary=True) as cursor:
            overall_query = "SELECT SUM(expense) AS total_spent, COUNT(*) AS total_transactions FROM expenses"
            cursor.execute(overall_query)
            overall = cursor.fetchone()

        total_spent = float(overall["total_spent"] or Decimal(0))
        total_transactions = int(overall["total_transactions"] or Decimal(0))

        overall_avg_monthly_spending = self.average_expense(year=year) or 0.0
        categories = self.spending_by_category(year=year, month=month)

        top_category = categories[0]["category"] if categories else None

        summary_data = {
            "total_spent_all_time": total_spent,
            "total_transactions": total_transactions,
            "overall_avg_monthly_spending": overall_avg_monthly_spending,
            "top_spending_category": top_category,
        }
        if year is None or month is None:
            return summary_data

        budget_data = self.remaining_budget(year=year, month=month)

        if budget_data is not None:
            monthly_budget = budget_data["total_budget"]
            monthly_spent = budget_data["total_spent"]
            remaining = budget_data["remaining"]
            is_over = remaining < 0
        else:
            monthly_budget = None
            remaining = None
            is_over = None
            monthly_spent = 0.0

            months = self.monthly_spending(year=year)

            match = next((m for m in months if m["month"] == month), None)
            monthly_spent = match["total_spent"] if match else 0.0

        summary_data["monthly_spent"] = monthly_spent
        summary_data["monthly_budget"] = monthly_budget
        summary_data["remaining_budget"] = remaining
        summary_data["is_over_budget"] = is_over

        return summary_data
