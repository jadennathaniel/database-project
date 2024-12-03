import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    'user': 'cs5330',
    'password': 'pw5330',
    'host': 'localhost',
}

def initialize_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS ProgramEvaluation;")
        cursor.execute("USE ProgramEvaluation;")

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

        connection.commit()
        print("Database and tables created successfully.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

# Run the script
if __name__ == "__main__":
    initialize_database()
