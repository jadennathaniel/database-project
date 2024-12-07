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
                level VARCHAR(50) NOT NULL,
                UNIQUE(name, level)
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
                year INT NOT NULL DEFAULT 2024,
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
                is_complete BOOLEAN NOT NULL DEFAULT FALSE,
                FOREIGN KEY (section_id) REFERENCES Sections(section_id),
                FOREIGN KEY (goal_id) REFERENCES Goals(goal_id)
            );
        """)

        # Create DegreeCourses table (Many-to-Many relationship)
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS DegreeCourses (
                degree_id INT NOT NULL,
                course_id INT NOT NULL,
                core BOOLEAN NOT NULL DEFAULT FALSE,  -- New column for "Core Course"
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
    if not name or name.strip() == "":
        raise ValueError("Degree name cannot be empty.")
    if not level or level.strip() == "":
        raise ValueError("Degree level cannot be empty.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM Degrees WHERE name = %s AND level = %s', (name, level))
        if cursor.fetchone()[0] > 0:
            raise ValueError(f"The combination of degree name '{name}' and level '{level}' already exists.")

        cursor.execute('INSERT INTO Degrees (name, level) VALUES (%s, %s)', (name, level))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        raise e
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


def add_course(course_number, name, degree_ids, is_core=False):
    if not isinstance(degree_ids, list):
        raise ValueError("degree_ids must be a list")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Courses (course_number, name) VALUES (%s, %s)', 
                       (course_number, name))
        course_id = cursor.lastrowid

        for degree_id in degree_ids:
            cursor.execute('SELECT degree_id FROM Degrees WHERE degree_id = %s', (degree_id,))
            if cursor.fetchone() is None:
                raise ValueError(f"Degree ID {degree_id} does not exist")
            cursor.execute('''
                INSERT INTO DegreeCourses (course_id, degree_id, core) 
                VALUES (%s, %s, %s)
            ''', (course_id, degree_id, is_core))

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


def add_section(course_id, section_number, semester, instructor_id, students_enrolled, year):
    if not section_number.isdigit() or len(section_number) != 3:
        raise ValueError("Section number must be 3 digits")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Sections 
            (course_id, section_number, semester, instructor_id, students_enrolled, year)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (course_id, section_number, semester, instructor_id, students_enrolled, year))
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

def get_all_goals():    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT g.*, d.name as degree_name, d.level as degree_level
            FROM Goals g
            JOIN Degrees d ON g.degree_id = d.degree_id
        ''')
        goals = cursor.fetchall()
        return goals
        
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

def get_instructor_sections(instructor_id, semester, year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT s.*, c.course_number, c.name as course_name
            FROM Sections s
            JOIN Courses c ON s.course_id = c.course_id
            WHERE s.instructor_id = %s 
            AND s.semester = %s
            AND s.year = %s
        ''', (instructor_id, semester, year))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_section_evaluations(section_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT e.*, g.code as goal_code, g.description as goal_description,
                   d.name as degree_name, d.level as degree_level
            FROM Evaluations e
            JOIN Goals g ON e.goal_id = g.goal_id
            JOIN Degrees d ON g.degree_id = d.degree_id
            WHERE e.section_id = %s
        ''', (section_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_section_goals(section_id):
    """Get all goals that need evaluation for this section"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        print(f"Getting goals for section {section_id}")  # Debug log
        
        cursor.execute('''
            SELECT DISTINCT g.*, d.name as degree_name, d.level as degree_level
            FROM Sections s
            JOIN Courses c ON s.course_id = c.course_id
            JOIN CourseGoals cg ON c.course_id = cg.course_id
            JOIN Goals g ON cg.goal_id = g.goal_id
            JOIN Degrees d ON g.degree_id = d.degree_id
            WHERE s.section_id = %s
        ''', (section_id,))
        
        goals = cursor.fetchall()
        print(f"Found {len(goals)} goals")  # Debug log
        return goals
        
    except Exception as e:
        print(f"Error getting goals: {e}")  # Debug log
        raise
    finally:
        cursor.close()
        conn.close()

def add_or_update_evaluation(section_id, goal_id, evaluation_method, 
                           num_a, num_b, num_c, num_f, improvement_notes=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Determine completion status
    filled_fields = sum(1 for field in [evaluation_method, num_a, num_b, num_c, num_f] if field)
    if filled_fields == 0:
        completion_status = 'not_entered'
    elif filled_fields < 5:
        completion_status = 'partially_completed'
    else:
        completion_status = 'completed'
        
    try:
        cursor.execute('''
            SELECT evaluation_id FROM Evaluations
            WHERE section_id = %s AND goal_id = %s
        ''', (section_id, goal_id))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE Evaluations 
                SET evaluation_method = %s,
                    grade_A = %s,
                    grade_B = %s,
                    grade_C = %s,
                    grade_F = %s,
                    improvement_notes = %s,
                    is_complete = %s
                WHERE section_id = %s AND goal_id = %s
            ''', (evaluation_method, num_a, num_b, num_c, num_f,
                  improvement_notes, completion_status, section_id, goal_id))
        else:
            cursor.execute('''
                INSERT INTO Evaluations (
                    section_id, goal_id, evaluation_method,
                    grade_A, grade_B, grade_C, grade_F,
                    improvement_notes, is_complete
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (section_id, goal_id, evaluation_method,
                  num_a, num_b, num_c, num_f,
                  improvement_notes, completion_status))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_goal_completion_status(section_id, goal_id):
    """Get completion status for a specific goal"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT evaluation_method, grade_A, grade_B, grade_C, grade_F,
                improvement_notes, is_complete
            FROM Evaluations
            WHERE section_id = %s AND goal_id = %s
        ''', (section_id, goal_id))
        eval_data = cursor.fetchone()
        
        if not eval_data:
            return {
                'status': 'not_entered',
                'completed_fields': 0,
                'total_fields': 5,
                'has_improvement': False
            }
            
        filled_fields = sum(1 for field in [
            eval_data['evaluation_method'],
            eval_data['grade_A'],
            eval_data['grade_B'],
            eval_data['grade_C'],
            eval_data['grade_F']
        ] if field is not None)
        
        return {
            'status': eval_data['is_complete'],
            'completed_fields': filled_fields,
            'total_fields': 5,
            'has_improvement': bool(eval_data['improvement_notes'])
        }
        
    finally:
        cursor.close()
        conn.close()

def save_evaluation(section_id, goal_id, data):
    """Save or update evaluation data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Determine completion status
    filled_fields = sum(1 for field in [
        data['evaluation_method'],
        data['grade_A'],
        data['grade_B'],
        data['grade_C'],
        data['grade_F']
    ] if field)
    
    if filled_fields == 0:
        completion_status = 'not_entered'
    elif filled_fields < 5:
        completion_status = 'partially_completed'
    else:
        completion_status = 'completed'
    
    try:
        cursor.execute('''
            INSERT INTO Evaluations (
                section_id, goal_id, evaluation_method,
                grade_A, grade_B, grade_C, grade_F,
                improvement_notes, is_complete
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                evaluation_method = VALUES(evaluation_method),
                grade_A = VALUES(grade_A),
                grade_B = VALUES(grade_B),
                grade_C = VALUES(grade_C),
                grade_F = VALUES(grade_F),
                improvement_notes = VALUES(improvement_notes),
                is_complete = VALUES(is_complete)
        ''', (
            section_id, goal_id,
            data['evaluation_method'],
            data['grade_A'], data['grade_B'],
            data['grade_C'], data['grade_F'],
            data['improvement_notes'],
            completion_status
        ))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def duplicate_evaluation(from_goal_id, to_goal_id, section_id):
    """Copy evaluation from one goal to another"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT evaluation_method, grade_A, grade_B, grade_C, grade_F,
                   improvement_notes, is_complete
            FROM Evaluations
            WHERE section_id = %s AND goal_id = %s
        ''', (section_id, from_goal_id))
        
        source_eval = cursor.fetchone()
        if not source_eval:
            raise ValueError("Source evaluation not found")
            
        add_or_update_evaluation(
            section_id=section_id,
            goal_id=to_goal_id,
            evaluation_method=source_eval['evaluation_method'],
            num_a=source_eval['grade_A'],
            num_b=source_eval['grade_B'],
            num_c=source_eval['grade_C'],
            num_f=source_eval['grade_F'],
            improvement_notes=source_eval['improvement_notes']
        )
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_existing_evaluation(section_id, goal_id):
    """
    Get existing evaluation data for a section's goal
    Returns: Dictionary with evaluation data or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            SELECT evaluation_id,
                   evaluation_method,
                   grade_A,
                   grade_B,
                   grade_C,
                   grade_F,
                   improvement_notes,
                   is_complete
            FROM Evaluations
            WHERE section_id = %s AND goal_id = %s
        ''', (section_id, goal_id))
        
        eval_data = cursor.fetchone()
        
        if eval_data:
            filled_fields = sum(1 for field in [
                eval_data['evaluation_method'],
                eval_data['grade_A'],
                eval_data['grade_B'],
                eval_data['grade_C'],
                eval_data['grade_F']
            ] if field is not None)
            
            if filled_fields == 0:
                eval_data['is_complete'] = 'not_entered'
            elif filled_fields < 5:  # Not all required fields are filled
                eval_data['is_complete'] = 'partially_completed'
            else:
                eval_data['is_complete'] = 'completed'
                
        return eval_data
        
    finally:
        cursor.close()
        conn.close()

def get_evaluation_status(section_id):
    """Get completion status of evaluations for a section"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT 
                COUNT(*) as total_goals,
                SUM(CASE WHEN e.is_complete = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN e.is_complete = 'partially_completed' THEN 1 ELSE 0 END) as partial,
                SUM(CASE WHEN e.is_complete = 'not_entered' OR e.is_complete IS NULL THEN 1 ELSE 0 END) as not_entered
            FROM Evaluations e
            WHERE e.section_id = %s
        ''', (section_id,))
        
        status = cursor.fetchone()
        return {
            'total': status['total_goals'],
            'completed': status['completed'],
            'partial': status['partial'],
            'not_entered': status['not_entered']
        }
        
    finally:
        cursor.close()
        conn.close()

def get_course_degrees(course_id):
    """Get all degrees associated with a course"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT d.* 
            FROM Degrees d
            JOIN DegreeCourses dc ON d.degree_id = dc.degree_id
            WHERE dc.course_id = %s
        ''', (course_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def associate_course_degree(course_id, degree_ids):
    """
    Associate a course with one or more degrees
    Args:
        course_id (int): Course ID to associate
        degree_ids (list): List of degree IDs to associate with course
    """
    if not isinstance(degree_ids, list):
        degree_ids = [degree_ids]
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify course exists
        cursor.execute('SELECT course_id FROM Courses WHERE course_id = %s', (course_id,))
        if not cursor.fetchone():
            raise ValueError(f"Course ID {course_id} does not exist")
            
        # Verify all degrees exist
        for degree_id in degree_ids:
            cursor.execute('SELECT degree_id FROM Degrees WHERE degree_id = %s', (degree_id,))
            if not cursor.fetchone():
                raise ValueError(f"Degree ID {degree_id} does not exist")
                
        # Check existing associations
        for degree_id in degree_ids:
            cursor.execute('''
                SELECT 1 FROM DegreeCourses 
                WHERE course_id = %s AND degree_id = %s
            ''', (course_id, degree_id))
            if cursor.fetchone():
                print(f"Course {course_id} already associated with degree {degree_id}")
                continue
                
            # Create new association
            cursor.execute('''
                INSERT INTO DegreeCourses (course_id, degree_id)
                VALUES (%s, %s)
            ''', (course_id, degree_id))
            
        conn.commit()
        print(f"Successfully associated course {course_id} with degrees {degree_ids}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error associating course with degrees: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()