from datetime import datetime

from expense_tracker.analysis import ExpenseAnalytics
from expense_tracker.database import BudgetManager, ExpenseManager

# Create objects
expense_manager = ExpenseManager()
budget_manager = BudgetManager()
analytics = ExpenseAnalytics(expense_manager)


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


def view_expenses():
    expenses = expense_manager.get_all_expenses()

    if not expenses:
        print("No expenses found.")
        return

    for expense in expenses:
        print(expense)


def search_expense():
    expense_id = int(input("Enter expense ID: "))
    expense = expense_manager.get_expense(expense_id)

    if expense:
        print(expense)
    else:
        print("Expense not found.")


def delete_expense():
    expense_id = int(input("Enter expense ID: "))

    if expense_manager.delete_expense(expense_id):
        print("Expense deleted.")
    else:
        print("Expense not found.")


def set_budget():
    year = int(input("Enter year: "))
    month = int(input("Enter month (1-12): "))
    amount = float(input("Enter budget amount: "))

    if budget_manager.set_budget(year, month, amount):
        print("Budget saved.")
    else:
        print("Budget was not changed.")


def view_budgets():
    budgets = budget_manager.get_budgets()

    if not budgets:
        print("No budgets found.")
        return

    for budget in budgets:
        print(budget)


def delete_budget():
    year = int(input("Enter year: "))
    month = int(input("Enter month (1-12): "))

    if budget_manager.delete_budget(year, month):
        print("Budget deleted.")
    else:
        print("Budget not found.")


def spending_by_category():
    year = input("Enter year (press Enter for all years): ")
    month = input("Enter month (press Enter for all months): ")

    results = analytics.spending_by_category(
        int(year) if year else None, int(month) if month else None
    )

    if not results:
        print("No expense data found.")
    else:
        for item in results:
            print(item)


def monthly_spending():
    year = input("Enter year (press Enter for all years): ")

    results = analytics.monthly_spending(int(year) if year else None)

    if not results:
        print("No expense data found.")
    else:
        for item in results:
            print(item)


def remaining_budget():
    year = int(input("Enter year: "))
    month = int(input("Enter month: "))

    result = analytics.remaining_budget(year, month)

    if result is None:
        print("No budget found for this month.")
    else:
        print("Total budget:", result["total_budget"])
        print("Total spent:", result["total_spent"])
        print("Remaining:", result["remaining"])

        if analytics.is_over_budget(year, month):
            print("Warning: You are over budget.")
        else:
            print("You are within your budget.")


def expense_summary():
    year = input("Enter year (press Enter to skip): ")
    month = input("Enter month (press Enter to skip): ")

    result = analytics.summary(
        int(year) if year else None, int(month) if month else None
    )

    if result is None:
        print("No expense data found.")
    else:
        for key, value in result.items():
            print(key.replace("_", " ").title() + ":", value)


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


if __name__ == "__main__":
    main()
