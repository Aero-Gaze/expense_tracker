import pymysql
from dotenv import load_dotenv
from os import getenv

# Load settings from .env file
load_dotenv()

# Database settings
DB_CONFIG = {
    "host": getenv("DB_HOST", "localhost"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "database": getenv("DB_NAME", "project_db"),
}


# Connect to database and create tables
class DatabaseManager:
    def __init__(self):
        self.create_tables()

    def get_connection(self):
        return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

    def create_tables(self):

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                # Create expenses table
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

                # Create budgets table
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


# Manage expenses
class ExpenseManager(DatabaseManager):
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
                    (name, category, expense, date.date(), description),
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

        query = "SELECT * FROM expenses WHERE 1=1"
        values = []

        if year is not None:
            query += " AND YEAR(date) = %s"
            values.append(year)

        if month is not None:
            query += " AND MONTH(date) = %s"
            values.append(month)

        query += " ORDER BY date DESC"

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)

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


# Manage budgets
class BudgetManager(DatabaseManager):
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

        query = "SELECT * FROM budgets WHERE 1=1"
        values = []

        if year is not None:
            query += " AND year = %s"
            values.append(year)

        if month is not None:
            query += " AND month = %s"
            values.append(month)

        query += " ORDER BY year, month"

        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)

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
