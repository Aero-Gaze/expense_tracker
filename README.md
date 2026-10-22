# Expense Tracker

A simple command-line expense tracker built with Python to record expenses, manage monthly budgets, and analyze spending through a MariaDB database.

## Features

- **Expense Management:** Add, list, view, and delete expense records.
- **Budget Management:** Set, view, and remove monthly budgets.
- **Spending Analytics:** Analyze expenses by category and month.
- **Budget Tracking:** Check remaining budgets and identify overspending.
- **Financial Summaries:** View total spending, transaction counts, average monthly spending, and top spending categories.
- **Date Filtering:** Filter expenses and analytics by year and month.
- **Terminal Interface:** Display results in formatted tables using Typer and Rich.

## Tech Stack

- **Language:** Python 3.14+
- **CLI Framework:** Typer
- **Database:** MariaDB
- **Database Connector:** MariaDB Connector/Python
- **Environment Configuration:** python-dotenv
- **Terminal Formatting:** Rich
- **Package Management:** uv

## Project Structure

```text
expense_tracker/
├── data/
│   ├── expenses.db
│   └── random_data_gen.py
├── src/
│   └── expense_tracker/
│       ├── __init__.py
│       ├── __main__.py
│       ├── analysis.py
│       ├── database.py
│       └── cli/
│           ├── __init__.py
│           ├── app.py
│           ├── expense.py
│           ├── budget.py
│           └── analysis.py
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

### Directory Overview

| File or directory | Purpose |
| --- | --- |
| `src/expense_tracker/cli/expense.py` | Expense management commands |
| `src/expense_tracker/cli/budget.py` | Monthly budget commands |
| `src/expense_tracker/cli/analysis.py` | Spending analytics commands |
| `src/expense_tracker/database.py` | Database connections and CRUD operations |
| `src/expense_tracker/analysis.py` | Financial calculations and summaries |
| `src/expense_tracker/cli/app.py` | Main CLI application and command registration |
| `data/random_data_gen.py` | Sample expense and budget data generator |
| `pyproject.toml` | Project metadata and dependencies |
| `uv.lock` | Locked dependency versions |

## Prerequisites

Before getting started, ensure you have:

- Python 3.14 or later
- [uv](https://docs.astral.sh/uv/) installed
- A running MariaDB server
- A MariaDB database user with permission to create and modify tables

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Aero-Gaze/expense_tracker.git
cd expense_tracker
```

### 2. Install dependencies

Install the project and its dependencies using uv:

```bash
uv sync
```

### 3. Configure the database

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=project_db
```

Replace the example credentials with your MariaDB configuration.

The application reads these environment variables when connecting to the database. `DB_HOST` defaults to `localhost`, and `DB_NAME` defaults to `project_db` when omitted.

**Note:** The database itself must already exist, and the configured user must have appropriate permissions. When the application starts, it creates the `expenses` and `budgets` tables if they do not already exist.

### 4. Start the application

```bash
uv run expense-tracker --help
```

This displays the available command groups and their usage.

You can also run the application through Python:

```bash
uv run python -m expense_tracker
```

## Usage

The application organizes its commands into three groups: `expense`, `budget`, and `analysis`.

### Expense Management

**Add an expense**

```bash
uv run expense-tracker expense add "Coffee" Dining 4.50
```

Add an expense with a specific date and description:

```bash
uv run expense-tracker expense add "Groceries" Food 45.75 \
  --date 2026-10-22 \
  --description "Weekly grocery shopping"
```

The date is optional and defaults to the current date. Supported date formats are `YYYY-MM-DD` and `DD/MM/YYYY`.

**List all expenses**

```bash
uv run expense-tracker expense list
```

**Filter expenses by year**

```bash
uv run expense-tracker expense list --year 2026
```

**Filter expenses by month**

```bash
uv run expense-tracker expense list --year 2026 --month 10
```

**View an expense by ID**

```bash
uv run expense-tracker expense list-by-id 1
```

**Delete an expense**

```bash
uv run expense-tracker expense remove 1
```

### Budget Management

**Set a budget for the current month**

```bash
uv run expense-tracker budget set 2500
```

**Set a budget for a specific month**

```bash
uv run expense-tracker budget set 2500 --year 2026 --month 10
```

Setting a budget for an existing month updates its amount.

**List budgets**

```bash
uv run expense-tracker budget list
```

**Filter budgets by year and month**

```bash
uv run expense-tracker budget list --year 2026 --month 10
```

**Remove a budget**

```bash
uv run expense-tracker budget remove --year 2026 --month 10
```

When setting or removing a budget, the current month and year are used by default. If you specify a year or month manually, provide both together.

### Spending Analytics

**Analyze spending by category**

```bash
uv run expense-tracker analysis category
```

Filter category spending by year and month:

```bash
uv run expense-tracker analysis category --year 2026 --month 10
```

**View monthly spending**

```bash
uv run expense-tracker analysis monthly
```

Filter monthly spending by year:

```bash
uv run expense-tracker analysis monthly --year 2026
```

**Check the remaining budget**

```bash
uv run expense-tracker analysis variance --year 2026 --month 10
```

**Check whether spending exceeds the budget**

```bash
uv run expense-tracker analysis over-budget --year 2026 --month 10
```

**Calculate average monthly spending**

```bash
uv run expense-tracker analysis average
```

Calculate the average for a particular year:

```bash
uv run expense-tracker analysis average --year 2026
```

**Display a financial summary**

```bash
uv run expense-tracker analysis summary
```

Display a summary for a specific month:

```bash
uv run expense-tracker analysis summary --year 2026 --month 10
```

For a full list of options for any command group, run:

```bash
uv run expense-tracker expense --help
uv run expense-tracker budget --help
uv run expense-tracker analysis --help
```

## Database Schema

The application initializes two tables in MariaDB.

### `expenses`

Stores individual expense records.

| Column | Description |
| --- | --- |
| `id` | Unique expense identifier |
| `name` | Expense name or title |
| `category` | Expense category |
| `description` | Optional additional details |
| `expense` | Expense amount |
| `date` | Date of the expense |

### `budgets`

Stores monthly budget limits.

| Column | Description |
| --- | --- |
| `id` | Unique budget identifier |
| `year` | Budget year |
| `month` | Budget month, from 1 to 12 |
| `amount` | Budget amount |

Each year and month combination can have only one budget. The database also enforces non-negative expense and budget amounts.

## Development

To work on the project locally:

```bash
git clone https://github.com/Aero-Gaze/expense_tracker.git
cd expense_tracker
uv sync
uv run expense-tracker --help
```

The codebase separates CLI commands, database operations, and analytics logic to keep the application organized and maintainable.

## Future Improvements

Potential enhancements include:

- Automated unit and integration tests
- Exporting expenses to CSV
- Visual spending reports and charts
- Custom date-range filtering
- Improved database configuration and error handling

---

Built with Python.
