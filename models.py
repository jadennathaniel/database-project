from db import get_db_connection
from mysql.connector import Error


def create_tables():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS ProgramEvaluation;")
        cursor.execute("USE ProgramEvaluation;")
        print("Using database: ProgramEvaluation")

        # Create Degrees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Degrees (
                degree_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                level VARCHAR(50) NOT NULL
            );
        """)

        # Create Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Courses (
                course_id INT AUTO_INCREMENT PRIMARY KEY,
                course_number VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL
            );
        """)

        # Create Instructors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Instructors (
                instructor_id CHAR(8) PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );
        """)

        # Create Sections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sections (
                section_id INT AUTO_INCREMENT PRIMARY KEY,
                course_id INT NOT NULL,
                semester VARCHAR(50) NOT NULL,
                section_number CHAR(3) NOT NULL,
                instructor_id CHAR(8),
                students_enrolled INT NOT NULL,
                FOREIGN KEY (course_id) REFERENCES Courses(course_id),
                FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id)
            );
        """)

        # Create Goals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Goals (
                goal_id INT AUTO_INCREMENT PRIMARY KEY,
                degree_id INT NOT NULL,
                code CHAR(4) NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY (degree_id) REFERENCES Degrees(degree_id)
            );
        """)

        # Create Evaluations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Evaluations (
                evaluation_id INT AUTO_INCREMENT PRIMARY KEY,
                section_id INT NOT NULL,
                goal_id INT NOT NULL,
                evaluation_method VARCHAR(100),
                grade_A INT DEFAULT 0,
                grade_B INT DEFAULT 0,
                grade_C INT DEFAULT 0,
                grade_F INT DEFAULT 0,
                improvement_notes TEXT,
                FOREIGN KEY (section_id) REFERENCES Sections(section_id),
                FOREIGN KEY (goal_id) REFERENCES Goals(goal_id)
            );
        """)

        # Create DegreeCourses table (Many-to-Many relationship)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS DegreeCourses (
                degree_id INT NOT NULL,
                course_id INT NOT NULL,
                PRIMARY KEY (degree_id, course_id),
                FOREIGN KEY (degree_id) REFERENCES Degrees(degree_id),
                FOREIGN KEY (course_id) REFERENCES Courses(course_id)
            );
        """)

        # Create CourseGoals table (Many-to-Many relationship)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CourseGoals (
                course_id INT NOT NULL,
                goal_id INT NOT NULL,
                PRIMARY KEY (course_id, goal_id),
                FOREIGN KEY (course_id) REFERENCES Courses(course_id),
                FOREIGN KEY (goal_id) REFERENCES Goals(goal_id)
            );
        """)

        conn.commit()
        print("Database and tables created successfully.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed.")


def add_degree(name, level):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Degrees (name, level) VALUES (%s, %s)', (name, level))
        conn.commit()
    except Error as e:
        print(f"Error adding degree: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_degrees():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Degrees')
    degrees = cursor.fetchall()
    cursor.close()
    conn.close()
    return degrees


def add_course(course_number, name, degree_ids):
    if not isinstance(degree_ids, list):
        raise ValueError("degree_ids must be a list")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Courses (course_number, name) VALUES (%s, %s)', (course_number, name))
        course_id = cursor.lastrowid
        
        for degree_id in degree_ids:
            cursor.execute('SELECT degree_id FROM Degrees WHERE degree_id = %s', (degree_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Degree ID {degree_id} does not exist")
            cursor.execute('INSERT INTO DegreeCourses (course_id, degree_id) VALUES (%s, %s)', (course_id, degree_id))
        
        conn.commit()
    except Error as e:
        print(f"Error adding course: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def add_instructor(instructor_id, name):
    if not (isinstance(instructor_id, str) and len(instructor_id) == 8):
        raise ValueError("instructor_id must be an 8-character string")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Instructors (instructor_id, name) VALUES (%s, %s)', 
                      (instructor_id, name))
        conn.commit()
    except Error as e:
        print(f"Error adding instructor: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_all_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Courses')
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return courses


def get_all_instructors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Instructors')
    instructors = cursor.fetchall()
    cursor.close()
    conn.close()
    return instructors


def add_section(course_id, section_number, semester, instructor_id, students_enrolled):
    if not section_number.isdigit() or len(section_number) != 3:
        raise ValueError("Section number must be 3 digits")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Sections 
            (course_id, section_number, semester, instructor_id, students_enrolled)
            VALUES (%s, %s, %s, %s, %s)
        ''', (course_id, section_number, semester, instructor_id, students_enrolled))
        conn.commit()
    except Error as e:
        print(f"Error adding section: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def add_goal(degree_id, code, description):
    if not code or len(code) != 4:
        raise ValueError("Goal code must be exactly 4 characters")
    if not description:
        raise ValueError("Description is required")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Goals (degree_id, code, description) VALUES (%s, %s, %s)', 
                       (degree_id, code, description))
        conn.commit()
    except Error as e:
        print(f"Error adding goal: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def associate_course_goal(course_id, goal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT course_id FROM Courses WHERE course_id = %s', (course_id,))
        if cursor.fetchone() is None:
            raise ValueError(f"Course ID {course_id} does not exist")
        
        cursor.execute('SELECT goal_id FROM Goals WHERE goal_id = %s', (goal_id,))
        if cursor.fetchone() is None:
            raise ValueError(f"Goal ID {goal_id} does not exist")
        
        cursor.execute('INSERT INTO CourseGoals (course_id, goal_id) VALUES (%s, %s)', (course_id, goal_id))
        conn.commit()
    except Error as e:
        print(f"Error associating course with goal: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
