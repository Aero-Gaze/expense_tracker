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
