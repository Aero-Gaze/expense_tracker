CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    description TEXT,
    expense DECIMAL(10, 2) NOT NULL CHECK (expense >= 0),
    date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL CHECK (year BETWEEN 1 AND 9999),
    month INT NOT NULL CHECK (month BETWEEN 1 and 12),
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),

    UNIQUE(year, month)
);
