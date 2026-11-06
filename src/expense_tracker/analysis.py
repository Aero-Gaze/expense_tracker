class ExpenseAnalytics:
    def __init__(self, db_manager):
        self.db = db_manager

    # Get total spending in each category
    def spending_by_category(self, year=None, month=None):

        query = """
            SELECT category,
                   SUM(expense) AS total_spent,
                   COUNT(*) AS transaction_count
            FROM expenses
            WHERE 1=1
        """

        values = []

        if year is not None:
            query += " AND YEAR(date) = %s"
            values.append(year)

        if month is not None:
            query += " AND MONTH(date) = %s"
            values.append(month)

        query += " GROUP BY category ORDER BY total_spent DESC"

        connection = self.db.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                return cursor.fetchall()

        finally:
            connection.close()

    # Get total spending for each month
    def monthly_spending(self, year=None):

        query = """
            SELECT YEAR(date) AS year,
                   MONTH(date) AS month,
                   SUM(expense) AS total_spent,
                   COUNT(*) AS transaction_count
            FROM expenses
        """

        values = []

        if year is not None:
            query += " WHERE YEAR(date) = %s"
            values.append(year)

        query += " GROUP BY year, month ORDER BY year DESC, month"

        connection = self.db.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
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

        connection = self.db.get_connection()

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

    # Check whether spending is over budget
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
        """

        values = []

        if year is not None:
            query += " WHERE YEAR(date) = %s"
            values.append(year)

        query += """
                GROUP BY YEAR(date), MONTH(date)
            ) AS monthly_expenses
        """

        connection = self.db.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()

                if result is None:
                    return None

                return result["average_spending"]

        finally:
            connection.close()

    # Get complete expense summary
    def summary(self, year=None, month=None):

        connection = self.db.get_connection()

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

        # Get total spending and transactions
        total_spent = float(result["total_spent"] or 0)
        total_transactions = result["total_transactions"]

        # Get average monthly spending
        average = self.average_expense(year) or 0

        # Get spending by category
        categories = self.spending_by_category(year, month)

        # Find the category with the highest spending
        if categories:
            top_category = categories[0]["category"]
        else:
            top_category = None

        # Store summary information
        summary = {
            "total_spent_all_time": total_spent,
            "total_transactions": total_transactions,
            "overall_avg_monthly_spending": average,
            "top_spending_category": top_category,
        }

        # Add budget information if year and month are provided
        if year is None or month is None:
            return summary

        budget = self.remaining_budget(year, month)

        if budget is not None:
            monthly_spent = budget["total_spent"]
            monthly_budget = budget["total_budget"]
            remaining = budget["remaining"]

            over_budget = remaining < 0

        else:
            monthly_budget = None
            remaining = None
            over_budget = None

            # Find spending for the selected month
            monthly_spent = 0

            months = self.monthly_spending(year)

            for item in months:
                if item["month"] == month:
                    monthly_spent = item["total_spent"]
                    break

        # Add monthly information
        summary["monthly_spent"] = monthly_spent
        summary["monthly_budget"] = monthly_budget
        summary["remaining_budget"] = remaining
        summary["is_over_budget"] = over_budget

        return summary
