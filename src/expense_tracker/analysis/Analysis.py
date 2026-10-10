from expense_tracker.database.Database import DatabaseManager


class ExpenseAnalytics:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def spending_by_category(self) -> list[dict]:
        """Returns category wise spending and count."""
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
        """Returns total monthly spending per year."""
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

    def remaining_budget(self, year: int, month: int) -> float | None:
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
        remaining = self.remaining_budget(year=year, month=month)
        if remaining is None:
            return None
        return remaining < 0

    def average_expense(self) -> list[dict]:
        """Returns the average expense for all month(s) and year(s)."""

        query = """
        SELECT ROUND(AVG(monthly_totals.total_spent), 2) AS overall_avg_monthly_spending
        FROM (
            SELECT 
            strftime('%Y-%m', date) AS month_year,
            SUM(expense) AS total_spent
            FROM expenses
            GROUP BY month_year
        ) AS monthly_totals;
            """

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def summary(self, year: int | None, month: int | None) -> dict:
        """Returns a comprehensive financial summary."""

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            overall_query = "SELECT SUM(expense) AS total_spent, COUNT(*) AS total_transactions FROM expenses"

            overall_query_res = cursor.execute(overall_query).fetchone()

            total_spent = float(overall_query_res["total_spent"] or 0)
            total_transactions = int(overall_query_res["total_transactions"] or 0)

            average_spending = self.average_expense()
            overall_avg_monthly_spending = (
                average_spending[0]["overall_avg_monthly_spending"]
                if average_spending
                else None
            )

            categories = self.spending_by_category()
            top_category = categories[0]["category"] if categories else None

            summary_data = {
                "total_spent_all_time": total_spent,
                "total_transactions": total_transactions,
                "overall_avg_monthly_spending": overall_avg_monthly_spending,
                "top_spending_category": top_category,
            }

            if year is not None and month is not None:
                monthly_expense_query = """
                SELECT SUM(expense) AS monthly_spent FROM expenses
                WHERE CAST(strftime('%Y', date) AS INTEGER) = ? AND CAST(strftime('%m', date) AS INTEGER) = ?
                    """

                monthly_expense_query_res = cursor.execute(
                    monthly_expense_query, (year, month)
                ).fetchone()
                monthly_spent = float(monthly_expense_query_res["monthly_spent"])

                budget_query = "SELECT amount FROM budget WHERE year = ? AND month = ?"
                budget_query_res = cursor.execute(
                    budget_query, (year, month)
                ).fetchone()
                monthly_budget = (
                    float(budget_query_res["amount"]) if budget_query_res else None
                )

                summary_data["period"] = {"year": year, "month": month}
                summary_data["monthly_spent"] = monthly_spent
                summary_data["monthly_budget"] = monthly_budget
                summary_data["variance"] = self.remaining_budget(year, month)
                summary_data["is_over_budget"] = self.is_over_budget(year, month)
            return summary_data
        finally:
            conn.close()
