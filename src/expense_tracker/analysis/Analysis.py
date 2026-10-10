from expense_tracker.database.Database import DatabaseManager


class ExpenseAnalytics:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def spending_by_category(
        self, year: int | None = None, month: int | None = None
    ) -> list[dict] | None:
        """Returns category wise spending and count, optionally filtered by year and/or month."""
        query = """
        SELECT category,
        sum(expense) as total_spent,
        COUNT(expense) as transaction_count
        FROM expenses WHERE 1=1
        """
        params = []

        if year is not None:
            query += " AND CAST(strftime('%Y', date) AS INTEGER) = ?"
            params.append(year)
        if month is not None:
            query += " AND CAST(strftime('%m', date) AS INTEGER) = ?"
            params.append(month)

        query += " GROUP BY category ORDER BY total_spent DESC"

        conn = self.db.get_connection()
        try:
            result = conn.execute(query, params).fetchall()
            if not result:
                return None
            return [dict(row) for row in result]

        finally:
            conn.close()

    def monthly_spending(self, year: int | None = None) -> list[dict] | None:
        """Returns total monthly spending per year, optionally filtered by year."""
        query = """
        SELECT
        CAST(strftime('%Y', date) AS INTEGER) AS year,
        CAST(strftime('%m', date) AS INTEGER) AS month,
        SUM(expense) as total_spent
        FROM expenses WHERE 1=1
        """
        params = []

        if year is not None:
            query += " AND year = ?"
            params.append(year)

        query += " GROUP BY year, month ORDER BY year, month DESC"

        conn = self.db.get_connection()
        try:
            result = conn.execute(query, params).fetchall()
            if not result:
                return None
            return [dict(row) for row in result]
        finally:
            conn.close()

    def remaining_budget(self, year: int, month: int) -> tuple[float, ...] | None:
        """Returns (total_budget, total_spent, total_budget - total_spent), or None if no budget exists."""
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

            total_spent = float(spent_result[0] or 0.0)

            variance = total_budget - total_spent
            return (total_budget, total_spent, variance)
        finally:
            conn.close()

    def is_over_budget(self, year: int, month: int) -> bool | None:
        """Returns True if over budget, or None if budget does not exist."""
        remaining = self.remaining_budget(year=year, month=month)
        if remaining is None:
            return None
        variance = remaining[2]
        return variance < 0

    def average_expense(self, year: int | None = None) -> dict | None:
        """Returns the average expense for a particular or all the years."""

        query = """
        SELECT ROUND(AVG(monthly_totals.total_spent), 2) AS overall_avg_monthly_spending
        FROM (
            SELECT 
            strftime('%Y-%m', date) AS month_year,
            SUM(expense) AS total_spent
            FROM expenses
            GROUP BY month_year
        ) AS monthly_totals
        WHERE 1=1
            """
        params = []

        if year is not None:
            query += " AND CAST(substr(month_year, 1, 4) AS INTEGER) = ?"
            params.append(year)

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query, params).fetchone()
            if rows and rows["overall_avg_monthly_spending"] is None:
                return None
            return dict(rows)
        finally:
            conn.close()

    def summary(self, year: int | None, month: int | None) -> dict:
        """Returns a comprehensive financial summary."""

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            overall_query = "SELECT SUM(expense) AS total_spent, COUNT(*) AS total_transactions FROM expenses"

            overall_query_res = cursor.execute(overall_query).fetchone()
        finally:
            conn.close()

        total_spent = float(overall_query_res["total_spent"] or 0)
        total_transactions = int(overall_query_res["total_transactions"] or 0)

        average_spending_dict = self.average_expense(year=year)
        overall_avg_monthly_spending = (
            average_spending_dict.get("overall_avg_monthly_spending")
            if average_spending_dict
            else 0.0
        )

        categories = self.spending_by_category(year=year, month=month)
        top_category = categories[0]["category"] if categories else None

        summary_data = {
            "total_spent_all_time": total_spent,
            "total_transactions": total_transactions,
            "overall_avg_monthly_spending": overall_avg_monthly_spending,
            "top_spending_category": top_category,
        }

        if year is not None and month is not None:
            budget_data = self.remaining_budget(year=year, month=month)
            if budget_data is not None:
                monthly_budget, monthly_spent, remaining = budget_data
                is_over = remaining < 0
            else:
                monthly_budget = None
                monthly_spent = 0.0

                months = self.monthly_spending(year=year)
                if months:
                    match = next((m for m in months if m["month"] == month), None)
                    if match:
                        monthly_spent = match["total_spent"]
                remaining = None
                is_over = None

            summary_data["period"] = {"year": year, "month": month}
            summary_data["monthly_spent"] = monthly_spent
            summary_data["monthly_budget"] = monthly_budget
            summary_data["remaining_budget"] = remaining
            summary_data["is_over_budget"] = is_over

        return summary_data
