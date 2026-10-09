from expense_tracker.database.database import DatabaseManager


class ExpenseAnalytics:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def spending_by_category(self) -> list[dict]:
        """Returns: [(category, total_spent, transaction_count), ...]"""
        query = """
        SELECT category,
        sum(expense) as total_spent,
        COUNT(expense) as transaction_count
        FROM expenses
        GROUP BY category 
        ORDER BY total_spent DESC
        """

        conn = self.db.get_connection()
        try:
            result = conn.execute(query).fetchall()
            return [dict(row) for row in result]
        finally:
            conn.close()

    def monthly_spending(self) -> list[dict]:
        """Returns: [(year, month, total_spent), ...]"""
        query = """
        SELECT
        CAST(strftime('%Y', date) AS INTEGER) AS year,
        CAST(strftime('%m', date) AS INTEGER) AS month,
        SUM(expense) as total_spent
        FROM expenses
        GROUP BY year, month
        ORDER BY year, month
        """

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def budget_vs_actual(self, year: int, month: int) -> float | None:
        """Returns remaining budget (total_budget - total_spent), or None if no budget exists."""
        budget_query = "SELECT amount FROM budget WHERE year = ? AND month = ?"
        expense_query = """
                SELECT
                SUM(expense)
                FROM expenses
                WHERE 
                CAST(strftime('%Y', date) AS INTEGER) = ?
                AND CAST(strftime('%m', date) AS INTEGER) = ?
                """

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            budget_result = cursor.execute(budget_query, (year, month)).fetchone()

            if budget_result is None:
                return None
            total_budget = float(budget_result["amount"])

            spent_result = cursor.execute(expense_query, (year, month)).fetchone()

            total_spent = float(spent_result[0])

            return total_budget - total_spent
        finally:
            conn.close()

    def is_over_budget(self, year: int, month: int) -> bool | None:
        """Returns True if over budget, or None if budget does not exist."""
        remaining = self.budget_vs_actual(year=year, month=month)
        if remaining is None:
            return None
        return remaining < 0
