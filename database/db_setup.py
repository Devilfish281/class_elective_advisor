# database/db_setup.py

import csv
import logging
import os
import sqlite3

import bcrypt  # Ensure bcrypt is installed: potery add bcrypt

logger = logging.getLogger(__name__)  # Reuse the global logger


def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logger.info(f"Connected to SQLite database: {db_file}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"SQLite connection error: {e}")
    return conn


def create_tables(conn):
    """Create tables in the SQLite database."""
    try:
        cursor = conn.cursor()
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Create Colleges Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Colleges (
                college_id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
            """
        )

        # Create Departments Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Departments (
                department_id INTEGER PRIMARY KEY,
                college_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (college_id) REFERENCES Colleges(college_id) ON DELETE CASCADE
            );
            """
        )

        # Create Degree_Levels Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Degree_Levels (
                degree_level_id INTEGER PRIMARY KEY,
                department_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE
            );
            """
        )

        # Create Degrees Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Degrees (
                degree_id INTEGER PRIMARY KEY,
                degree_level_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (degree_level_id) REFERENCES Degree_Levels(degree_level_id) ON DELETE CASCADE
            );
            """
        )

        # Create Requirements Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Requirements (
                requirement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                degree_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (degree_id) REFERENCES Degrees(degree_id) ON DELETE CASCADE
            );
            """
        )

        # Create Subcategories Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Subcategories (
                subcategory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (requirement_id) REFERENCES Requirements(requirement_id) ON DELETE CASCADE
            );
            """
        )

        # Create Courses Table
        """
        use the following subcategories to index the table
            1,1,Lower-Division Core
            2,1,Upper-Division Core
            3,1,Mathematics Requirements
            4,1,Science and Mathematics Electives
            5,1,Computer Science Electives        
        """

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subcategory_id INTEGER NOT NULL,
                course_code TEXT UNIQUE NOT NULL,  
                name TEXT NOT NULL,
                units INTEGER NOT NULL DEFAULT 3,
                description TEXT,
                prerequisites TEXT,
                FOREIGN KEY (subcategory_id) REFERENCES Subcategories(subcategory_id) ON DELETE CASCADE
            );
            """
        )

        # Create Users Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP                
            );            
       
            """
        )

        # Create Prerequisites Table referencing course_id instead of course_code
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Prerequisites (
                prerequisite_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                prerequisite_course_id INTEGER NOT NULL,
                FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
                FOREIGN KEY (prerequisite_course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
            );
            """
        )

        # Create User_Preferences Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS User_Preferences (
                preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                college_id INTEGER,
                department_id INTEGER,
                degree_level_id INTEGER,
                degree_id INTEGER,
                job_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (college_id) REFERENCES Colleges(college_id),
                FOREIGN KEY (department_id) REFERENCES Departments(department_id),
                FOREIGN KEY (degree_level_id) REFERENCES Degree_Levels(degree_level_id),
                FOREIGN KEY (degree_id) REFERENCES Degrees(degree_id),
                FOREIGN KEY (job_id) REFERENCES Jobs(job_id) ON DELETE SET NULL
            );
            """
        )

        # Create Recommendations Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Recommendations (
                recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                job_id INTEGER, 
                course_id INTEGER,
                rating REAL NOT NULL,
                explanation TEXT NOT NULL,
                rank INTEGER,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (job_id) REFERENCES Jobs(job_id) ON DELETE CASCADE, -- Foreign key constraint
                FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
            );
            """
        )

        # Create User_Interactions Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS User_Interactions (
                interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            );
            """
        )

        # Create Jobs Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Jobs (
                job_id INTEGER PRIMARY KEY,
                degree_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (degree_id) REFERENCES Degrees(degree_id) ON DELETE CASCADE
            );
            """
        )

        conn.commit()
        logger.info("All tables created successfully.")

    except sqlite3.Error as e:
        logger.error(f"An error occurred while creating tables: {e}")
        conn.rollback()


def populate_colleges_data(conn):
    """
    Populate the Colleges table from colleges.csv.
    The CSV file should be located in the same directory as this script.
    """
    try:
        cursor = conn.cursor()

        # Check if Colleges table is empty
        cursor.execute("SELECT COUNT(*) FROM Colleges;")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Colleges table already populated. Skipping CSV loading.")
            return  # Exit the function to prevent duplicate data insertion

        # Determine the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the colleges.csv file
        csv_file_path = os.path.join(script_dir, "colleges.csv")

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            logger.error(
                f"CSV file not found at {csv_file_path}. Please ensure the file exists."
            )
            return

        # Open and read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the required column exists
            if "college_id" not in reader.fieldnames or "name" not in reader.fieldnames:
                logger.error("CSV file must contain 'college_id' and 'name' columns.")
                return

            # Iterate over each row and insert into Colleges table
            for row in reader:
                college_id = row["college_id"].strip()
                college_name = row["name"].strip()

                if college_id and college_name:
                    if college_id.isdigit():
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO Colleges (college_id, name)
                            VALUES (?, ?);
                            """,
                            (int(college_id), college_name),
                        )
                        logger.info(
                            f"Inserted college: {college_name} with ID: {college_id}"
                        )
                    else:
                        logger.warning(
                            f"Invalid college_id '{college_id}' for college '{college_name}'. Skipping row."
                        )
                else:
                    logger.warning(
                        "Encountered empty 'college_id' or 'name' field. Skipping row."
                    )

        conn.commit()
        logger.info("Colleges table populated from colleges.csv successfully.")

    except FileNotFoundError:
        logger.error(
            f"CSV file not found at {csv_file_path}. Please ensure the file exists."
        )
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"An error occurred while populating Colleges: {e}")
        raise  # Re-raise exception after rollback


def populate_departments_data(conn):
    """
    Populate the Departments table from departments.csv.
    """
    try:
        cursor = conn.cursor()

        # Check if Departments table is empty
        cursor.execute("SELECT COUNT(*) FROM Departments;")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Departments table already populated. Skipping CSV loading.")
            return

        # Determine the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the departments.csv file
        csv_file_path = os.path.join(script_dir, "departments.csv")

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            logger.error(
                f"CSV file not found at {csv_file_path}. Please ensure the file exists."
            )
            return

        # Open and read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the required columns exist
            if (
                "department_id" not in reader.fieldnames
                or "college_id" not in reader.fieldnames
                or "name" not in reader.fieldnames
            ):
                logger.error(
                    "CSV file must contain 'department_id', 'college_id', and 'name' columns."
                )
                return

            # Iterate over each row and insert into Departments table
            for row in reader:
                department_id = row["department_id"].strip()
                college_id = row["college_id"].strip()
                department_name = row["name"].strip()

                if department_id and college_id and department_name:
                    if department_id.isdigit() and college_id.isdigit():
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO Departments (department_id, college_id, name)
                            VALUES (?, ?, ?);
                            """,
                            (int(department_id), int(college_id), department_name),
                        )
                        logger.info(
                            f"Inserted department: {department_name} with ID: {department_id} under College ID: {college_id}"
                        )
                    else:
                        logger.warning(
                            f"Invalid department_id '{department_id}' or college_id '{college_id}' for department '{department_name}'. Skipping row."
                        )
                else:
                    logger.warning(
                        "Encountered empty fields in departments.csv. Skipping row."
                    )

        conn.commit()
        logger.info("Departments table populated from departments.csv successfully.")

    except FileNotFoundError:
        logger.error(
            f"CSV file not found at {csv_file_path}. Please ensure the file exists."
        )
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"An error occurred while populating Departments: {e}")
        raise


def populate_degree_levels_data(conn):
    """
    Populate the Degree_Levels table from degree_levels.csv.
    """
    try:
        cursor = conn.cursor()

        # Check if Degree_Levels table is empty
        cursor.execute("SELECT COUNT(*) FROM Degree_Levels;")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Degree_Levels table already populated. Skipping CSV loading.")
            return

        # Determine the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the degree_levels.csv file
        csv_file_path = os.path.join(script_dir, "degree_levels.csv")

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            logger.error(
                f"CSV file not found at {csv_file_path}. Please ensure the file exists."
            )
            return

        # Open and read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the required columns exist
            if (
                "degree_level_id" not in reader.fieldnames
                or "department_id" not in reader.fieldnames
                or "name" not in reader.fieldnames
            ):
                logger.error(
                    "CSV file must contain 'degree_level_id', 'department_id', and 'name' columns."
                )
                return

            # Iterate over each row and insert into Degree_Levels table
            for row in reader:
                degree_level_id = row["degree_level_id"].strip()
                department_id = row["department_id"].strip()
                degree_level_name = row["name"].strip()

                if degree_level_id and department_id and degree_level_name:
                    if degree_level_id.isdigit() and department_id.isdigit():
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO Degree_Levels (degree_level_id, department_id, name)
                            VALUES (?, ?, ?);
                            """,
                            (
                                int(degree_level_id),
                                int(department_id),
                                degree_level_name,
                            ),
                        )
                        logger.info(
                            f"Inserted degree level: {degree_level_name} with ID: {degree_level_id} under Department ID: {department_id}"
                        )
                    else:
                        logger.warning(
                            f"Invalid degree_level_id '{degree_level_id}' or department_id '{department_id}' for degree level '{degree_level_name}'. Skipping row."
                        )
                else:
                    logger.warning(
                        "Encountered empty fields in degree_levels.csv. Skipping row."
                    )

        conn.commit()
        logger.info(
            "Degree_Levels table populated from degree_levels.csv successfully."
        )

    except FileNotFoundError:
        logger.error(
            f"CSV file not found at {csv_file_path}. Please ensure the file exists."
        )
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"An error occurred while populating Degree_Levels: {e}")
        raise


def populate_degrees_data(conn):
    """
    Populate the Degrees table from degrees.csv.
    """
    try:
        cursor = conn.cursor()

        # Check if Degrees table is empty
        cursor.execute("SELECT COUNT(*) FROM Degrees;")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Degrees table already populated. Skipping CSV loading.")
            return

        # Determine the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the degrees.csv file
        csv_file_path = os.path.join(script_dir, "degrees.csv")

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            logger.error(
                f"CSV file not found at {csv_file_path}. Please ensure the file exists."
            )
            return

        # Open and read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the required columns exist
            if (
                "degree_id" not in reader.fieldnames
                or "degree_level_id" not in reader.fieldnames
                or "name" not in reader.fieldnames
            ):
                logger.error(
                    "CSV file must contain 'degree_id', 'degree_level_id', and 'name' columns."
                )
                return

            # Iterate over each row and insert into Degrees table
            for row in reader:
                degree_id = row["degree_id"].strip()
                degree_level_id = row["degree_level_id"].strip()
                degree_name = row["name"].strip()

                if degree_id and degree_level_id and degree_name:
                    if degree_id.isdigit() and degree_level_id.isdigit():
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO Degrees (degree_id, degree_level_id, name)
                            VALUES (?, ?, ?);
                            """,
                            (int(degree_id), int(degree_level_id), degree_name),
                        )
                        logger.info(
                            f"Inserted degree: {degree_name} with ID: {degree_id} under Degree Level ID: {degree_level_id}"
                        )
                    else:
                        logger.warning(
                            f"Invalid degree_id '{degree_id}' or degree_level_id '{degree_level_id}' for degree '{degree_name}'. Skipping row."
                        )
                else:
                    logger.warning(
                        "Encountered empty fields in degrees.csv. Skipping row."
                    )

        conn.commit()
        logger.info("Degrees table populated from degrees.csv successfully.")

    except FileNotFoundError:
        logger.error(
            f"CSV file not found at {csv_file_path}. Please ensure the file exists."
        )
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"An error occurred while populating Degrees: {e}")
        raise


def populate_requirements_data(conn):
    """
    Populate the Requirements table from requirements.csv.
    """
    try:
        cursor = conn.cursor()

        # Check if Requirements table is empty
        cursor.execute("SELECT COUNT(*) FROM Requirements;")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Requirements table already populated. Skipping CSV loading.")
            return

        # Determine the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the requirements.csv file
        csv_file_path = os.path.join(script_dir, "requirements.csv")

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            logger.error(
                f"CSV file not found at {csv_file_path}. Please ensure the file exists."
            )
            return

        # Open and read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the required columns exist
            if (
                "requirement_id" not in reader.fieldnames
                or "degree_id" not in reader.fieldnames
                or "type" not in reader.fieldnames
                or "name" not in reader.fieldnames
            ):
                logger.error(
                    "CSV file must contain 'requirement_id', 'degree_id', 'type', and 'name' columns."
                )
                return

            # Iterate over each row and insert into Requirements table
            for row in reader:
                requirement_id = row["requirement_id"].strip()
                degree_id = row["degree_id"].strip()
                req_type = row["type"].strip()
                req_name = row["name"].strip()

                if requirement_id and degree_id and req_type and req_name:
                    if degree_id.isdigit():
                        cursor.execute(
                            """
                            INSERT INTO Requirements (degree_id, type, name)
                            VALUES (?, ?, ?);
                            """,
                            (int(degree_id), req_type, req_name),
                        )
                        logger.info(
                            f"Inserted requirement: {req_name} for Degree ID: {degree_id}"
                        )
                    else:
                        logger.warning(
                            f"Invalid degree_id '{degree_id}' for requirement '{req_name}'. Skipping row."
                        )
                else:
                    logger.warning(
                        "Encountered empty fields in requirements.csv. Skipping row."
                    )

        conn.commit()
        logger.info("Requirements table populated from requirements.csv successfully.")

    except FileNotFoundError:
        logger.error(
            f"CSV file not found at {csv_file_path}. Please ensure the file exists."
        )
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"An error occurred while populating Requirements: {e}")
        raise


def populate_subcategories_data(conn):
    """
    Populate the Subcategories table from subcategories.csv.
    """
    try:
        cursor = conn.cursor()

        # Check if Subcategories table is empty
        cursor.execute("SELECT COUNT(*) FROM Subcategories;")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Subcategories table already populated. Skipping CSV loading.")
            return

        # Determine the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the subcategories.csv file
        csv_file_path = os.path.join(script_dir, "subcategories.csv")

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            logger.error(
                f"CSV file not found at {csv_file_path}. Please ensure the file exists."
            )
            return

        # Open and read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the required columns exist
            if (
                "subcategory_id" not in reader.fieldnames
                or "requirement_id" not in reader.fieldnames
                or "name" not in reader.fieldnames
            ):
                logger.error(
                    "CSV file must contain 'subcategory_id', 'requirement_id', and 'name' columns."
                )
                return

            # Iterate over each row and insert into Subcategories table
            for row in reader:
                subcategory_id = row["subcategory_id"].strip()
                requirement_id = row["requirement_id"].strip()
                subcat_name = row["name"].strip()

                if subcategory_id and requirement_id and subcat_name:
                    if requirement_id.isdigit():
                        cursor.execute(
                            """
                            INSERT INTO Subcategories (requirement_id, name)
                            VALUES (?, ?);
                            """,
                            (int(requirement_id), subcat_name),
                        )
                        logger.info(
                            f"Inserted subcategory: {subcat_name} under Requirement ID: {requirement_id}"
                        )
                    else:
                        logger.warning(
                            f"Invalid requirement_id '{requirement_id}' for subcategory '{subcat_name}'. Skipping row."
                        )
                else:
                    logger.warning(
                        "Encountered empty fields in subcategories.csv. Skipping row."
                    )

        conn.commit()
        logger.info(
            "Subcategories table populated from subcategories.csv successfully."
        )

    except FileNotFoundError:
        logger.error(
            f"CSV file not found at {csv_file_path}. Please ensure the file exists."
        )
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"An error occurred while populating Subcategories: {e}")
        raise


def populate_courses_data(conn):
    """
    Populate the Courses table from courses.csv.
    Extracts 'course_code' and 'units' from the 'name' field if 'course_code' and 'units' columns are missing.
    """
    try:
        cursor = conn.cursor()

        # Check if Courses table is empty
        cursor.execute("SELECT COUNT(*) FROM Courses;")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Courses table already populated. Skipping CSV loading.")
            return

        # Determine the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the courses.csv file
        csv_file_path = os.path.join(script_dir, "courses.csv")

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            logger.error(
                f"CSV file not found at {csv_file_path}. Please ensure the file exists."
            )
            return

        # Open and read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Define required columns excluding 'course_code' and 'units'
            required_columns = {
                "course_id",
                "subcategory_id",
                "name",
                "description",
                "prerequisites",
            }

            # Check if the required columns exist
            missing_columns = required_columns - set(reader.fieldnames)
            if missing_columns:
                logger.error(
                    f"CSV file is missing the following required columns: {', '.join(missing_columns)}."
                )
                return

            # Iterate over each row and insert into Courses table
            for row in reader:
                course_id = row["course_id"].strip()
                subcategory_id = row["subcategory_id"].strip()
                full_name = row["name"].strip()
                course_description = row["description"].strip()
                prerequisites = row["prerequisites"].strip()

                # Initialize default values
                course_code = None
                course_name = None
                units = 3  # Default value as per the database schema

                # Attempt to parse 'course_code', 'course_name', and 'units' from 'full_name'
                try:
                    # Expected format: "CPSC 120, Introduction to Programming, (3)"
                    parts = [part.strip() for part in full_name.split(",")]
                    if len(parts) >= 3:
                        course_code = parts[0]  # e.g., "CPSC 120"
                        course_name = ", ".join(
                            parts[1:-1]
                        )  # e.g., "Introduction to Programming"
                        units_str = parts[-1].strip("() ")
                        if units_str.isdigit():
                            units = int(units_str)
                        else:
                            logger.warning(
                                f"Invalid units '{units_str}' for course '{course_code}'. Using default units: {units}."
                            )
                    elif len(parts) == 2:
                        course_code = parts[0]  # e.g., "CPSC 120"
                        course_name = parts[1]  # e.g., "Introduction to Programming"
                        # Units not provided; use default
                    else:
                        course_code = parts[0] if parts else None
                        course_name = full_name  # Use the entire name as course name
                except Exception as e:
                    logger.warning(
                        f"Failed to parse 'name' field '{full_name}' for course_id '{course_id}': {e}. Skipping row."
                    )
                    continue

                # Validate required fields
                if not all([course_id, subcategory_id, course_code, course_name]):
                    logger.warning(
                        "One or more required fields are missing in a row. Skipping row."
                    )
                    continue

                if not (course_id.isdigit() and subcategory_id.isdigit()):
                    logger.warning(
                        f"Invalid data types for course_id '{course_id}' or subcategory_id '{subcategory_id}'. Skipping row."
                    )
                    continue

                cursor.execute(
                    """
                    INSERT INTO Courses (subcategory_id, course_code, name, units, description, prerequisites)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        int(subcategory_id),
                        course_code,
                        course_name,
                        units,
                        course_description,
                        prerequisites,
                    ),
                )
                logger.info(
                    f"Inserted course: {course_name} ({course_code}) under Subcategory ID: {subcategory_id} with units: {units}"
                )

        conn.commit()
        logger.info("Courses table populated from courses.csv successfully.")

    except FileNotFoundError:
        logger.error(
            f"CSV file not found at {csv_file_path}. Please ensure the file exists."
        )
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error while populating Courses: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"An error occurred while populating Courses: {e}")
        raise


def populate_jobs_data(conn):
    """
    Populate the Jobs table from jobs.csv.
    """
    try:
        cursor = conn.cursor()

        # Check if Jobs table is empty
        cursor.execute("SELECT COUNT(*) FROM Jobs;")
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Jobs table already populated. Skipping CSV loading.")
            return

        # Determine the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the jobs.csv file
        csv_file_path = os.path.join(script_dir, "jobs.csv")

        # Check if the CSV file exists
        if not os.path.isfile(csv_file_path):
            logger.error(
                f"CSV file not found at {csv_file_path}. Please ensure the file exists."
            )
            return

        # Open and read the CSV file
        with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Check if the required columns exist
            required_columns = {"job_id", "degree_id", "name", "description"}
            if not required_columns.issubset(reader.fieldnames):
                logger.error(
                    f"CSV file must contain the following columns: {', '.join(required_columns)}."
                )
                return

            # Iterate over each row and insert into Jobs table
            for row in reader:
                job_id = row["job_id"].strip()
                degree_id = row["degree_id"].strip()
                job_name = row["name"].strip()
                job_description = row["description"].strip()

                if job_id and degree_id and job_name:
                    if job_id.isdigit() and degree_id.isdigit():
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO Jobs (job_id, degree_id, name, description)
                            VALUES (?, ?, ?, ?);
                            """,
                            (
                                int(job_id),
                                int(degree_id),
                                job_name,
                                job_description,
                            ),
                        )
                        logger.info(
                            f"Inserted job: {job_name} with ID: {job_id} under Degree ID: {degree_id}"
                        )
                    else:
                        logger.warning(
                            f"Invalid job_id '{job_id}' or degree_id '{degree_id}' for job '{job_name}'. Skipping row."
                        )
                else:
                    logger.warning(
                        "Encountered empty 'job_id', 'degree_id', or 'name' field in jobs.csv. Skipping row."
                    )

        conn.commit()
        logger.info("Jobs table populated from jobs.csv successfully.")

    except FileNotFoundError:
        logger.error(
            f"CSV file not found at {csv_file_path}. Please ensure the file exists."
        )
    except csv.Error as e:
        logger.error(f"Error reading CSV file: {e}")
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error while populating Jobs: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"An error occurred while populating Jobs: {e}")
        raise


def main_int_db():
    logger.info("Starting database setup...")
    database = "smart_elective_advisor.db"

    # Define the db directory path (at the current level)
    db_directory = os.path.join(os.getcwd(), "db")

    # Ensure the db directory exists, if not, create it
    if not os.path.exists(db_directory):
        os.makedirs(db_directory)
        logger.info(f"Created directory for database at {db_directory}")

    # Define the database path inside the db directory
    db_path = os.path.join(db_directory, database)

    # Create a database connection
    conn = create_connection(db_path)

    if conn is not None:
        try:
            # Create tables
            create_tables(conn)

            # Populate Colleges from CSV
            populate_colleges_data(conn)

            # Populate Departments from CSV
            populate_departments_data(conn)

            # Populate Degree Levels from CSV
            populate_degree_levels_data(conn)

            # Populate Degrees from CSV
            populate_degrees_data(conn)

            # Populate Requirements from CSV
            populate_requirements_data(conn)

            # Populate Subcategories from CSV
            populate_subcategories_data(conn)

            # Populate Courses from CSV
            populate_courses_data(conn)

            # Populate Jobs from CSV
            populate_jobs_data(conn)

            # Additional population functions can be added here

        except Exception as e:
            logger.error(f"An error occurred during database setup: {e}")
        finally:
            # Close the connection
            conn.close()
            logger.info(f"Database setup completed. Database file: {db_path}")
    else:
        logger.error("Error! Cannot create the database connection.")
