# database/db_operations.py

import os
import sqlite3


def connect_db():
    db_path = os.getenv("DATABASE_PATH", "electives.db")
    conn = sqlite3.connect(db_path)
    return conn


def insert_elective(
    number, course_code, course_name, rating, prerequisites, explanation
):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO electives (number, course_code, course_name, rating, prerequisites, explanation)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
        (number, course_code, course_name, rating, prerequisites, explanation),
    )
    conn.commit()
    conn.close()


def fetch_all_electives():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM electives")
    rows = cursor.fetchall()
    conn.close()
    return rows
