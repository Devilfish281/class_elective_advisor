# database/db_setup.py

import os
import sqlite3


def main_int_db():
    print("Setting up the database...")

    # Define the db directory path (at the current level)
    db_directory = os.path.join(os.getcwd(), "db")

    # Ensure the db directory exists, if not, create it
    if not os.path.exists(db_directory):
        os.makedirs(db_directory)

    # Define the database path inside the db directory
    db_path = os.path.join(db_directory, os.getenv("DATABASE_PATH", "electives.db"))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create electives table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS electives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number INTEGER,
        course_code TEXT NOT NULL,
        course_name TEXT NOT NULL,
        rating INTEGER,
        prerequisites TEXT,
        explanation TEXT
    )
    """
    )

    conn.commit()
    conn.close()
    print(f"Database setup completed. Database file: {db_path}")
