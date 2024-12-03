-- Create Database
CREATE DATABASE ProgramEvaluation;

USE ProgramEvaluation;

-- Degrees Table
CREATE TABLE Degrees (
    degree_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    level VARCHAR(50) NOT NULL
);

-- Courses Table
CREATE TABLE Courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Instructors Table
CREATE TABLE Instructors (
    instructor_id CHAR(8) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Sections Table
CREATE TABLE Sections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    semester VARCHAR(50) NOT NULL,
    section_number CHAR(3) NOT NULL,
    instructor_id CHAR(8),
    students_enrolled INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id)
);

-- Goals Table
CREATE TABLE Goals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    degree_id INT NOT NULL,
    code CHAR(4) NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (degree_id) REFERENCES Degrees(degree_id)
);

-- Evaluations Table
CREATE TABLE Evaluations (
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

-- DegreeCourses Table (Many-to-Many relationship)
CREATE TABLE DegreeCourses (
    degree_id INT NOT NULL,
    course_id INT NOT NULL,
    PRIMARY KEY (degree_id, course_id),
    FOREIGN KEY (degree_id) REFERENCES Degrees(degree_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
