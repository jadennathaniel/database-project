from flask import jsonify, render_template, request, redirect, url_for, flash
from app import app
from models import add_degree, add_course, add_instructor, add_or_update_evaluation, add_section, add_goal, associate_course_degree, associate_course_goal, duplicate_evaluation, get_all_goals, get_course_degrees, get_degrees, get_all_courses, get_all_instructors, get_evaluation_status, get_existing_evaluation, get_goal_completion_status, get_instructor_sections, get_section_evaluations, get_section_goals

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_degree', methods=['GET', 'POST'])
def add_degree_route():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        level = request.form.get('level', '').strip()

        try:
            add_degree(name, level)
            flash('Degree added successfully!', 'success')
            return redirect(url_for('index'))
        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash('An unexpected error occurred. Please try again.', 'error')

    return render_template('add_degree.html')


@app.route('/add_course', methods=['GET', 'POST'])
def add_course_route():
    degrees = get_degrees()
    if request.method == 'POST':
        course_number = request.form['course_number']
        name = request.form['name']
        degree_ids = request.form.getlist('degree_ids')
        is_core = 'is_core' in request.form 
        try:
            add_course(course_number, name, degree_ids, is_core)
            flash('Course added successfully!', 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')

    return render_template('add_course.html', degrees=degrees)


@app.route('/add_instructor', methods=['GET', 'POST'])
def add_instructor_route():
    if request.method == 'POST':
        instructor_id = request.form.get('id', '').strip()
        name = request.form.get('name', '').strip()
        
        # Validate input
        if not instructor_id or not name:
            flash('Both ID and name are required', 'error')
            return render_template('add_instructor.html', 
                                instructor_id=instructor_id, 
                                name=name), 400
        
        if not len(instructor_id) == 8 or not instructor_id.isdigit():
            flash('Instructor ID must be exactly 8 digits', 'error')
            return render_template('add_instructor.html',
                                instructor_id=instructor_id,
                                name=name), 400

        try:
            add_instructor(instructor_id, name)
            flash(f'Successfully added instructor {name}', 'success')
            return redirect(url_for('index'))
            
        except ValueError as ve:
            flash(str(ve), 'error')
            return render_template('add_instructor.html',
                                instructor_id=instructor_id,
                                name=name), 400
                                
        except Exception as e:
            flash('An error occurred while adding the instructor', 'error')
            return render_template('add_instructor.html',
                                instructor_id=instructor_id,
                                name=name), 500
            
    return render_template('add_instructor.html')

@app.route('/add_section', methods=['GET', 'POST'])
def add_section_route():
    courses = get_all_courses()
    instructors = get_all_instructors()
    
    if request.method == 'POST':
        try:
            course_id = request.form.get('course_id')
            section_number = request.form.get('section_number', '').strip()
            semester = request.form.get('semester')
            instructor_id = request.form.get('instructor_id')
            students_enrolled = request.form.get('students_enrolled')
            year = request.form.get('year')

            if not all([course_id, section_number, semester, instructor_id, students_enrolled, year]):
                raise ValueError("All fields are required")
                
            add_section(course_id, section_number, semester, 
                       instructor_id, students_enrolled, year)
            flash('Section added successfully', 'success')
            return redirect(url_for('index'))
            
        except ValueError as e:
            print("Validation error:", str(e))
            flash(str(e), 'error')
        except Exception as e:
            print("Database error:", str(e))
            flash('Error adding section', 'error')
            
    return render_template('add_section.html', 
                         courses=courses,
                         instructors=instructors)

@app.route('/add_goal', methods=['GET', 'POST'])
def add_goal_route():
    # Get all degrees for dropdown
    degrees = get_degrees()
    
    if request.method == 'POST':
        try:
            degree_id = request.form.get('degree_id', '').strip()
            print(degree_id)
            code = request.form.get('code', '').strip()
            print(code)
            description = request.form.get('description', '').strip()
            print(description)

            # Validate required fields
            if not all([degree_id, code, description]):
                raise ValueError("All fields are required")

            # Validate code format
            if len(code) != 4:
                raise ValueError("Goal code must be exactly 4 characters")

            add_goal(degree_id, code, description)
            flash('Goal added successfully', 'success')
            return redirect(url_for('index'))

        except ValueError as e:
            flash(str(e), 'error')
            return render_template('add_goal.html',
                                degrees=degrees,
                                code=code,
                                description=description), 400
                                
        except Exception as e:
            flash('An error occurred while adding the goal', 'error')
            return render_template('add_goal.html',
                                degrees=degrees,
                                code=code, 
                                description=description), 500

    return render_template('add_goal.html', degrees=degrees)

@app.route('/associate_course_goal', methods=['GET', 'POST'])
def associate_course_goal_route():
    if request.method == 'GET':
        courses = get_all_courses()
        goals = get_all_goals()
        return render_template('associate_course_goal.html',
                             courses=courses,
                             goals=goals)
                             
    elif request.method == 'POST':
        try:
            course_id = request.form.get('course_id')
            goal_id = request.form.get('goal_id')
            
            if not all([course_id, goal_id]):
                raise ValueError("Course and goal must be selected")
                
            associate_course_goal(course_id, goal_id)
            flash('Course-goal association created successfully', 'success')
            return redirect(url_for('index'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('associate_course_goal_route'))
        except Exception as e:
            flash('Error creating association', 'error')
            return redirect(url_for('associate_course_goal_route'))

@app.route('/add_evaluation', methods=['GET', 'POST'])
def add_evaluation_route():
    if request.method == 'GET':
        semester = request.args.get('semester')
        instructor_id = request.args.get('instructor_id')
        section_id = request.args.get('section_id')
        year = request.args.get('year')
        
        sections = []
        goals = []
        goal_statuses = {}  # Track completion status per goal
        existing_data = {}  # Store existing evaluation data
        
        if semester and instructor_id:
            sections = get_instructor_sections(instructor_id, semester, year)
            
        if section_id:
            goals = get_section_goals(section_id)
            for goal in goals:
                # Get completion status for this goal
                status = get_goal_completion_status(section_id, goal['goal_id'])
                goal_statuses[goal['goal_id']] = status
                
                # Get existing evaluation data if any
                eval_data = get_existing_evaluation(section_id, goal['goal_id'])
                if eval_data:
                    existing_data[goal['goal_id']] = eval_data
        
        return render_template('add_evaluation.html',
                             sections=sections,
                             goals=goals,
                             goal_statuses=goal_statuses,
                             existing_data=existing_data,
                             semester=semester,
                             instructor_id=instructor_id,
                             section_id=section_id)
                             
    elif request.method == 'POST':
        try:
            section_id = request.form.get('section_id')
            goal_id = request.form.get('goal_id')
            save_as_draft = request.form.get('save_as_draft') == 'true'
            
            # Get form data
            data = {
                'evaluation_method': request.form.get('evaluation_method'),
                'grade_A': request.form.get('num_a', '0'),
                'grade_B': request.form.get('num_b', '0'),
                'grade_C': request.form.get('num_c', '0'),
                'grade_F': request.form.get('num_f', '0'),
                'improvement_suggestion': request.form.get('improvement', '')
            }
            
            # Convert grades to integers
            for grade in ['grade_A', 'grade_B', 'grade_C', 'grade_F']:
                try:
                    data[grade] = int(data[grade])
                except (ValueError, TypeError):
                    data[grade] = 0
            
            # Add or update evaluation
            add_or_update_evaluation(
                section_id=section_id,
                goal_id=goal_id,
                evaluation_method=data['evaluation_method'],
                num_a=data['grade_A'],
                num_b=data['grade_B'],
                num_c=data['grade_C'],
                num_f=data['grade_F'],
                improvement_suggestion=data['improvement_suggestion']
            )
            
            # Handle duplicate evaluations if requested
            duplicate_to = request.form.getlist('duplicate_to')
            for target_goal_id in duplicate_to:
                if target_goal_id != goal_id:
                    duplicate_evaluation(goal_id, target_goal_id, section_id)
            
            if save_as_draft:
                flash('Evaluation saved as draft', 'success')
            else:
                flash('Evaluation completed successfully', 'success')
                
            return redirect(url_for('add_evaluation_route',
                                  semester=request.form.get('semester'),
                                  instructor_id=request.form.get('instructor_id'),
                                  section_id=section_id))
                                  
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(request.url)
        except Exception as e:
            flash('Error saving evaluation', 'error')
            print(f"Error: {str(e)}")  # For debugging
            return redirect(request.url)

    return render_template('add_evaluation.html')
        
@app.route('/search_route', methods=['GET', 'POST'])
def search_route():
    if request.method == 'GET':
        print("SEARCH GOT")
    elif request.method == 'POST':
        print("SEARCH POST")

@app.route('/associate_course_degree', methods=['GET', 'POST'])
def associate_course_degree_route():
    if request.method == 'GET':
        courses = get_all_courses()
        degrees = get_degrees()
        return render_template('associate_course_degree.html',
                             courses=courses,
                             degrees=degrees)
                             
    elif request.method == 'POST':
        try:
            course_id = request.form.get('course_id')
            degree_ids = request.form.getlist('degree_ids')  # Handle multiple selections
            
            print(f"Received course_id: {course_id}")  # Debug log
            print(f"Received degree_ids: {degree_ids}")  # Debug log
            
            if not course_id:
                raise ValueError("Course must be selected")
            if not degree_ids:
                raise ValueError("At least one degree must be selected")
                
            # Convert to integers
            course_id = int(course_id)
            degree_ids = [int(d_id) for d_id in degree_ids]
                
            associate_course_degree(course_id, degree_ids)
            flash('Course-degree associations created successfully', 'success')
            
            # Redirect back to same page to show updated associations
            return redirect(url_for('associate_course_degree_route'))
            
        except ValueError as e:
            print(f"Validation error: {str(e)}")  # Debug log
            flash(str(e), 'error')
            return redirect(url_for('associate_course_degree_route'))
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # Debug log
            flash('Error creating association. Please try again.', 'error')
            return redirect(url_for('associate_course_degree_route'))
        
@app.route('/get_course_degrees/<int:course_id>')
def get_course_degrees_route(course_id):
    existing_degrees = get_course_degrees(course_id)
    return jsonify([d['degree_id'] for d in existing_degrees])