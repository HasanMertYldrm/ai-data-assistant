import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "workspace.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()

    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(trim(name)) > 0),
                age INTEGER CHECK(age IS NULL OR age BETWEEN 0 AND 120),
                department_id INTEGER NOT NULL,
                email TEXT UNIQUE,
                salary_try INTEGER CHECK(salary_try IS NULL OR salary_try >= 0),

                FOREIGN KEY (department_id)
                    REFERENCES departments(id)
                    ON DELETE RESTRICT
            );
        """)

        conn.executemany(
            "INSERT OR IGNORE INTO departments (name) VALUES (?)",
            [("Yazılım",), ("Satış",), ("Pazarlama",)]
        )

        conn.commit()

        print("Database initialized successfully!")

        print(
            "Departments:",
            conn.execute("SELECT * FROM departments").fetchall()
        )

        print(
            "Foreign keys enabled:",
            conn.execute("PRAGMA foreign_keys").fetchone()[0]
        )

    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()