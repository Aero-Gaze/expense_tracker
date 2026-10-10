from datetime import date, timedelta
import random
import sqlite3

# Sample pools for realistic data generation
CATEGORIES = {
    "Groceries": [
        "Supermarket haul",
        "Weekly vegetables",
        "Organic store run",
        "Bakery items",
    ],
    "Utilities": [
        "Electricity bill",
        "Water bill",
        "High-speed Internet",
        "Gas cylinder",
    ],
    "Dining": [
        "Coffee with team",
        "Weekend dinner",
        "Takeout lunch",
        "Boba tea",
    ],
    "Transportation": [
        "Fuel refill",
        "Metro pass",
        "Cab fare",
        "Parking fees",
    ],
    "Entertainment": [
        "Streaming subscription",
        "Movie tickets",
        "Concert ticket",
        "Video game purchase",
    ],
    "Shopping": ["New apparel", "Electronics accessory", "Home decor", "Books"],
}

CATEGORY_WEIGHTS = [0.25, 0.15, 0.20, 0.15, 0.10, 0.15]


def generate_data(
    db_path: str = "tracker.db",
    num_expenses: int = 100,
    start_year: int = 2025,
    end_year: int = 2026,
):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure schema exists
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            expense REAL NOT NULL CHECK (expense >= 0),
            date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 9999),
            month INTEGER NOT NULL CHECK (month BETWEEN 1 and 12),
            amount REAL NOT NULL CHECK (amount >= 0),

            UNIQUE(year, month)
        );
        """
    )

    # 1. Populate 'budget' table across target years/months
    budget_records = []
    for yr in range(start_year, end_year + 1):
        for mo in range(1, 13):
            # Monthly budget between 1,500.00 and 3,500.00
            monthly_budget = round(random.uniform(1500.0, 3500.0), 2)
            budget_records.append((yr, mo, monthly_budget))

    cursor.executemany(
        """
        INSERT OR IGNORE INTO budget (year, month, amount)
        VALUES (?, ?, ?)
        """,
        budget_records,
    )

    # 2. Populate 'expenses' table
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    time_span_days = (end_date - start_date).days

    categories = list(CATEGORIES.keys())
    expense_records = []

    for _ in range(num_expenses):
        cat = random.choices(categories, weights=CATEGORY_WEIGHTS, k=1)[0]
        desc = random.choice(CATEGORIES[cat])
        name = f"{cat} - {desc.split()[0]}"

        # Realistic expense scaling depending on category
        if cat == "Groceries":
            val = round(random.uniform(15.0, 180.0), 2)
        elif cat == "Utilities":
            val = round(random.uniform(40.0, 220.0), 2)
        elif cat == "Dining":
            val = round(random.uniform(8.0, 75.0), 2)
        elif cat == "Transportation":
            val = round(random.uniform(10.0, 60.0), 2)
        elif cat == "Entertainment":
            val = round(random.uniform(12.0, 120.0), 2)
        else:  # Shopping
            val = round(random.uniform(25.0, 300.0), 2)

        random_day = start_date + timedelta(days=random.randint(0, time_span_days))
        date_str = random_day.strftime("%Y-%m-%d")

        expense_records.append((name, cat, desc, val, date_str))

    cursor.executemany(
        """
        INSERT INTO expenses (name, category, description, expense, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        expense_records,
    )

    conn.commit()
    conn.close()
    print(
        f"Successfully inserted {len(budget_records)} budget rows and {num_expenses} expense records into '{db_path}'."
    )


if __name__ == "__main__":
    generate_data("expenses.db", num_expenses=150, start_year=2025, end_year=2026)
