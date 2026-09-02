import sqlite3
from pathlib import Path
DATABASE_PATH = Path("data/dnd.db")

def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def create_database():
    connection = get_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            normalized_name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            source TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            alias TEXT NOT NULL,
            normalized_alias TEXT NOT NULL UNIQUE,
            FOREIGN KEY (entry_id) REFERENCES entries(id)
        )
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_entries_normalized_name
        ON entries(normalized_name)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_aliases_normalized
        ON aliases(normalized_alias)
    """)

    connection.commit()
    connection.close()

if __name__ == "__main__":
    create_database()