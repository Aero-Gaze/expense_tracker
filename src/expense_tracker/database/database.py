from pathlib import Path

# Base locations
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parents[3]  # Equivalent to .parent.parent.parent.parent

# Resource paths
DB_DIR = BASE_DIR / "data"
DB_FILE = DB_DIR / "expenses.db"
SCHEMA_FILE = SRC_DIR / "schema.sql"


def init_db_dir() -> Path:
    """Ensures the database directory exists before returning its path."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_DIR
