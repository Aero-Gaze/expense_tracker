import sqlite3
from pathlib import Path

# Base locations
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parents[3]  # Equivalent to .parent.parent.parent.parent


# Resource paths
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = DB_DIR / "expenses.db"
SCHEMA_FILE = SRC_DIR / "schema.sql"


class Database:
    def __init__(self, db_path: Path, schema_path: Path) -> None:
        self.db_path: Path = db_path
        self.schema_path: Path = schema_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        query = self.schema_path.read_text(encoding="utf-8")
        with self.get_connection() as conn:
            conn.executescript(query)
