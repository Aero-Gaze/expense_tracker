from datetime import datetime

from expense_tracker.analysis import ExpenseAnalytics
from expense_tracker.database import BudgetManager, ExpenseManager

# Create objects
expense_manager = ExpenseManager()
budget_manager = BudgetManager()
analytics = ExpenseAnalytics(expense_manager)


def print_table(headers, rows):

    # Find the maximum width for each column
    widths = []

    for i in range(len(headers)):
        max_width = len(str(headers[i]))

        for row in rows:
            max_width = max(max_width, len(str(row[i])))

        widths.append(max_width + 2)  # Add spacing

    # Print headers
    for i in range(len(headers)):
        print(f"{headers[i]:<{widths[i]}}", end="")

    print()

    # Print separator
    for width in widths:
        print("-" * width, end="")

    print()

    # Print rows
    for row in rows:
        for i in range(len(row)):
            print(f"{str(row[i]):<{widths[i]}}", end="")

        print()


# Add expense
def add_expense():

    name = input("Enter expense name: ")
    category = input("Enter category: ")
    amount = float(input("Enter amount: "))
    date = datetime.strptime(input("Enter date (YYYY-MM-DD): "), "%Y-%m-%d")
    description = input("Enter description (optional): ")

    expense_id = expense_manager.add_expense(
        name, category, amount, date, description or None
    )

    print("Expense added. ID:", expense_id)


# View all expenses
def view_expenses():

    expenses = expense_manager.get_all_expenses()

    if not expenses:
        print("No expenses found.")
        return

    rows = []

    for expense in expenses:
        rows.append(
            [
                expense["id"],
                expense["name"],
                expense["category"],
                expense["expense"],
                expense["date"],
                expense["description"] or "-",
            ]
        )

    print_table(["ID", "Name", "Category", "Amount", "Date", "Description"], rows)


# Search expense
def search_expense():

    expense_id = int(input("Enter expense ID: "))
    expense = expense_manager.get_expense(expense_id)

    if not expense:
        print("Expense not found.")
        return

    rows = [
        [
            expense["id"],
            expense["name"],
            expense["category"],
            expense["expense"],
            expense["date"],
            expense["description"] or "-",
        ]
    ]

    print_table(["ID", "Name", "Category", "Amount", "Date", "Description"], rows)


# Delete expense
def delete_expense():

    expense_id = int(input("Enter expense ID: "))

    if expense_manager.delete_expense(expense_id):
        print("Expense deleted.")
    else:
        print("Expense not found.")


# Set budget
def set_budget():

    year = int(input("Enter year: "))
    month = int(input("Enter month (1-12): "))
    amount = float(input("Enter budget amount: "))

    if budget_manager.set_budget(year, month, amount):
        print("Budget saved.")
    else:
        print("Budget was not changed.")


# View budgets
def view_budgets():

    budgets = budget_manager.get_budgets()

    if not budgets:
        print("No budgets found.")
        return

    rows = []

    for budget in budgets:
        rows.append([budget["id"], budget["year"], budget["month"], budget["amount"]])

    print_table(["ID", "Year", "Month", "Budget"], rows)


# Delete budget
def delete_budget():

    year = int(input("Enter year: "))
    month = int(input("Enter month (1-12): "))

    if budget_manager.delete_budget(year, month):
        print("Budget deleted.")
    else:
        print("Budget not found.")


# View spending by category
def spending_by_category():

    year = input("Enter year (press Enter for all years): ")
    month = input("Enter month (press Enter for all months): ")

    results = analytics.spending_by_category(
        int(year) if year else None, int(month) if month else None
    )

    if not results:
        print("No expense data found.")
        return

    rows = []

    for item in results:
        rows.append([item["category"], item["total_spent"], item["transaction_count"]])

    print_table(["Category", "Total Spent", "Transactions"], rows)


# View monthly spending
def monthly_spending():

    year = input("Enter year (press Enter for all years): ")

    results = analytics.monthly_spending(int(year) if year else None)

    if not results:
        print("No expense data found.")
        return

    rows = []

    for item in results:
        rows.append(
            [
                item["year"],
                item["month"],
                item["total_spent"],
                item["transaction_count"],
            ]
        )

    print_table(["Year", "Month", "Total Spent", "Transactions"], rows)


# View remaining budget
def remaining_budget():

    year = int(input("Enter year: "))
    month = int(input("Enter month: "))

    result = analytics.remaining_budget(year, month)

    if result is None:
        print("No budget found for this month.")
        return

    rows = [[result["total_budget"], result["total_spent"], result["remaining"]]]

    print_table(["Total Budget", "Total Spent", "Remaining"], rows)

    if analytics.is_over_budget(year, month):
        print("Warning: You are over budget!")
    else:
        print("You are within your budget.")


# View expense summary
def expense_summary():

    year = input("Enter year (press Enter to skip): ")
    month = input("Enter month (press Enter to skip): ")

    result = analytics.summary(
        int(year) if year else None, int(month) if month else None
    )

    if not result:
        print("No expense data found.")
        return

    rows = []

    for key, value in result.items():
        rows.append(
            [key.replace("_", " ").title(), value if value is not None else "-"]
        )

    print_table(["Description", "Value"], rows)


# Main menu
def main():

    try:
        while True:
            print("\n========== EXPENSE TRACKER ==========")
            print("1. Add Expense")
            print("2. View All Expenses")
            print("3. Search Expense by ID")
            print("4. Delete Expense")
            print("5. Set Monthly Budget")
            print("6. View Budgets")
            print("7. Delete Budget")
            print("8. View Spending by Category")
            print("9. View Monthly Spending")
            print("10. View Remaining Budget")
            print("11. View Expense Summary")
            print("0. Exit")

            choice = input("\nEnter your choice: ")

            try:
                if choice == "1":
                    add_expense()

                elif choice == "2":
                    view_expenses()

                elif choice == "3":
                    search_expense()

                elif choice == "4":
                    delete_expense()

                elif choice == "5":
                    set_budget()

                elif choice == "6":
                    view_budgets()

                elif choice == "7":
                    delete_budget()

                elif choice == "8":
                    spending_by_category()

                elif choice == "9":
                    monthly_spending()

                elif choice == "10":
                    remaining_budget()

                elif choice == "11":
                    expense_summary()

                elif choice == "0":
                    print("Exiting...")
                    break

                else:
                    print("Invalid choice. Please try again.")

            except ValueError:
                print("Invalid input. Please enter the correct value.")

            except Exception as error:
                print("An error occurred:", error)

    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting safely.")

    finally:
        print("Thank you for using Expense Tracker!")


if __name__ == "__main__":
    main()
