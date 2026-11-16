import os
from datetime import datetime

from expense_tracker.expense_manager import ExpenseManager

# Create expense manager
expense_manager = ExpenseManager()


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def fancy_printing(function):

    clear_screen()

    try:
        function()

    except ValueError:
        print("\nInvalid input. Please enter the correct value.")

    except Exception as e:
        print(f"Error occurred: {e}")

    input("\nPress Enter key to return to main menu...")

    clear_screen()


# Print a table
def print_table(headers, rows):

    # Find column widths
    widths = []

    for i in range(len(headers)):
        width = len(str(headers[i]))

        for row in rows:
            if len(str(row[i])) > width:
                width = len(str(row[i]))

        widths.append(width + 2)

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

    if description == "":
        description = None

    expense_id = expense_manager.add_expense(name, category, amount, date, description)

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

    if expense is None:
        print("Expense not found.")
        return

    rows = []

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


# Delete expense
def delete_expense():

    expense_id = int(input("Enter expense ID: "))

    result = expense_manager.delete_expense(expense_id)

    if result:
        print("Expense deleted.")
    else:
        print("Expense not found.")


# Set budget
def set_budget():

    year = int(input("Enter year: "))
    month = int(input("Enter month (1-12): "))
    amount = float(input("Enter budget amount: "))

    result = expense_manager.set_budget(year, month, amount)

    if result:
        print("Budget saved.")
    else:
        print("Budget was not changed.")


# View budgets
def view_budgets():

    budgets = expense_manager.get_budgets()

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

    result = expense_manager.delete_budget(year, month)

    if result:
        print("Budget deleted.")
    else:
        print("Budget not found.")


# View spending by category
def spending_by_category():

    year = input("Enter year (press Enter for all years): ")
    month = input("Enter month (press Enter for all months): ")

    if year == "":
        year = None
    else:
        year = int(year)

    if month == "":
        month = None
    else:
        month = int(month)

    results = expense_manager.spending_by_category(year, month)

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

    if year == "":
        year = None
    else:
        year = int(year)

    results = expense_manager.monthly_spending(year)

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

    result = expense_manager.remaining_budget(year, month)

    if result is None:
        print("No budget found for this month.")
        return

    rows = []

    rows.append([result["total_budget"], result["total_spent"], result["remaining"]])

    print_table(["Total Budget", "Total Spent", "Remaining"], rows)

    if result["remaining"] < 0:
        print("Warning: You are over budget!")
    else:
        print("You are within your budget.")


# View expense summary
def expense_summary():

    year = input("Enter year (press Enter to skip): ")
    month = input("Enter month (press Enter to skip): ")

    if year == "":
        year = None
    else:
        year = int(year)

    if month == "":
        month = None
    else:
        month = int(month)

    result = expense_manager.summary(year, month)

    rows = []

    for key, value in result.items():
        name = key.replace("_", " ").title()

        if value is None:
            value = "-"

        rows.append([name, value])

    print_table(["Description", "Value"], rows)


# Main menu
def main():
    clear_screen()
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

            if choice == "1":
                fancy_printing(add_expense)

            elif choice == "2":
                fancy_printing(view_expenses)

            elif choice == "3":
                fancy_printing(search_expense)

            elif choice == "4":
                fancy_printing(delete_expense)

            elif choice == "5":
                fancy_printing(set_budget)

            elif choice == "6":
                fancy_printing(view_budgets)

            elif choice == "7":
                fancy_printing(delete_budget)

            elif choice == "8":
                fancy_printing(spending_by_category)

            elif choice == "9":
                fancy_printing(monthly_spending)

            elif choice == "10":
                fancy_printing(remaining_budget)

            elif choice == "11":
                fancy_printing(expense_summary)

            elif choice == "0":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")
                clear_screen()

    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting safely.")


if __name__ == "__main__":
    main()
