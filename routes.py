from datetime import datetime
from flask import jsonify, render_template, request, redirect, url_for, flash
from app import app
from models import ( add_degree, add_course, add_instructor, add_or_update_evaluation, add_section, add_goal, associate_course_degree, associate_course_goal, 
                    get_all_evaluations, get_all_goals, get_all_sections, get_course_degrees, get_courses_by_goals, get_degree, 
                    get_degree_courses, get_degree_goals, get_degree_sections, get_degrees, get_all_courses, get_all_instructors, 
                    get_existing_evaluation, get_goal_completion_status, get_instructor_sections, get_section_goals, 
                    get_instructor_sections_single, get_sections_evaluation_status, get_goals_for_course )

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
        try:
            semester = request.args.get('semester')
            instructor_id = request.args.get('instructor_id')
            section_id = request.args.get('section_id')
            year = request.args.get('year')

            sections = []
            goals = []
            goal_statuses = {}
            existing_data = {}
            other_degrees = get_degrees()

            if semester and instructor_id:
                sections = get_instructor_sections_single(instructor_id, semester, year)

            if section_id:
                goals = get_section_goals(section_id)
                for goal in goals:
                    status = get_goal_completion_status(section_id, goal['goal_id'])
                    goal_statuses[goal['goal_id']] = status
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
                                section_id=section_id,
                                year=year,
                                other_degrees=other_degrees)

        except Exception as e:
            print(f"Error in GET: {str(e)}")
            flash(str(e), 'error')
            return redirect(url_for('index'))

    elif request.method == 'POST':
        try:
            section_id = request.form.get('section_id')
            goal_id = request.form.get('goal_id')
            evaluation_method = request.form.get('evaluation_method')
            
            # Convert empty strings to None for grades
            num_a = request.form.get('num_a')
            num_a = int(num_a) if num_a != '' else None
            
            num_b = request.form.get('num_b')
            num_b = int(num_b) if num_b != '' else None
            
            num_c = request.form.get('num_c')
            num_c = int(num_c) if num_c != '' else None
            
            num_f = request.form.get('num_f')
            num_f = int(num_f) if num_f != '' else None
            
            improvement = request.form.get('improvement', '')

            # Check if all required fields are filled
            required_fields = [
                evaluation_method,
                num_a is not None,
                num_b is not None,
                num_c is not None,
                num_f is not None
            ]
            
            # Set completion status based on required fields
            is_complete = 'completed' if all(required_fields) else 'partially_completed'

            add_or_update_evaluation(
                section_id=section_id,
                goal_id=goal_id,
                evaluation_method=evaluation_method,
                num_a=num_a,
                num_b=num_b,
                num_c=num_c,
                num_f=num_f,
                improvement_notes=improvement,
                is_complete=is_complete
            )

            flash('Evaluation saved successfully', 'success')
            return redirect(url_for('add_evaluation_route',
                                  semester=request.args.get('semester'),
                                  instructor_id=request.args.get('instructor_id'),
                                  section_id=section_id))
        except Exception as e:
            print(f"Error in POST: {str(e)}")
            flash(str(e), 'error')
            return redirect(request.url)

    # Default return for unexpected method
    return render_template('add_evaluation.html')

        
from flask import request

@app.route('/search_route', methods=['GET'])
def search_route():
    filter_type = request.args.get('filter_type', '').strip().lower()

    # If no filter_type provided or invalid one
    if not filter_type or filter_type not in ['degree', 'course', 'instructor', 'section', 'goal', 'evaluation']:
        return "No valid filter type selected."

    # DEGREE FILTER
    if filter_type == 'degree':
        degree_name = request.args.get('degree_name', '').strip()
        all_degrees = get_degrees()  # Returns a list of dicts with keys like 'degree_id', 'name', 'level'
        
        filtered_degrees = []
        for d in all_degrees:
            # If a degree_name filter is present, only include degrees that match
            if degree_name and degree_name.lower() not in d['name'].lower():
                continue
            filtered_degrees.append(d)
        
        return render_template('search_results.html', results=filtered_degrees, filter_type='degree')

    # COURSE FILTER
    elif filter_type == 'course':
        course_number = request.args.get('course_number', '').strip()
        from_semester = request.args.get('from_semester_course', '').strip()  # currently unused
        to_semester = request.args.get('to_semester_course', '').strip()      # currently unused

        all_courses = get_all_courses()  # Returns a list of dicts, e.g. {'course_id':..., 'course_number':..., 'name':..., 'is_core':...}
        all_sections = get_all_sections()  # Returns a list of dicts, e.g. {'section_id':..., 'course_id':..., 'semester':..., 'year':...}

        def semester_to_tuple(semester):
            """Convert semester string to a tuple (year, semester) for comparison."""
            sem, year = semester.split()
            sem_order = {'spring': 1, 'summer': 2, 'fall': 3}
            return (int(year), sem_order[sem.lower()])

        filtered_sections = []
        for c in all_courses:
            # Filter by course_number if provided
            if course_number and course_number.lower() not in c['course_number'].lower():
                continue

            # Filter sections by course_id and semester range
            for s in all_sections:
                if s['course_id'] == c['course_id']:
                    if from_semester and to_semester:
                        from_sem_tuple = semester_to_tuple(from_semester)
                        to_sem_tuple = semester_to_tuple(to_semester)
                        section_sem_tuple = semester_to_tuple(f"{s['semester']} {s['year']}")
                        if from_sem_tuple <= section_sem_tuple <= to_sem_tuple:
                            filtered_sections.append({
                                'course_number': c['course_number'],
                                'course_name': c['name'],
                                'section_number': s['section_number'],
                                'semester': s['semester'],
                                'year': s['year'],
                                'instructor_name': s.get('instructor_name', 'N/A'),
                                'students_enrolled': s.get('students_enrolled', 'N/A')
                            })
                    else:
                        filtered_sections.append({
                            'course_number': c['course_number'],
                            'course_name': c['name'],
                            'section_number': s['section_number'],
                            'semester': s['semester'],
                            'year': s['year'],
                            'instructor_name': s.get('instructor_name', 'N/A'),
                            'students_enrolled': s.get('students_enrolled', 'N/A')
                        })

        return render_template('search_results.html', results=filtered_sections, filter_type='course')
    
    # INSTRUCTOR FILTER
    elif filter_type == 'instructor':
        instructor_id = request.args.get('instructor_id', '').strip()
        from_semester = request.args.get('from_semester_instructor', '').strip()
        from_year = request.args.get('from_year_instructor', '').strip()
        to_semester = request.args.get('to_semester_instructor', '').strip()
        to_year = request.args.get('to_year_instructor', '').strip()

        # Check that all necessary parameters are provided
        if not instructor_id:
            return "Please provide an instructor_id."
        if not from_semester or not to_semester or not from_year or not to_year:
            return "Please provide from_semester_instructor, from_year_instructor, to_semester_instructor, and to_year_instructor."

        try:
            # Fetch sections taught by the instructor in the given semester/year range
            sections = get_instructor_sections(instructor_id, from_semester, from_year, to_semester, to_year)
            return render_template('search_results.html', results=sections, filter_type='section')
        except ValueError as ve:
            return str(ve), 400
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again later.", 500

    # SECTION FILTER
    elif filter_type == 'section':
        section_number = request.args.get('section_number', '').strip()
        from_semester = request.args.get('from_semester_section', '').strip() # currently unused
        to_semester = request.args.get('to_semester_section', '').strip()     # currently unused

        all_sections_data = get_all_sections() # Returns a list of dicts for all sections
        
        filtered_sections = []
        for s in all_sections_data:
            # Filter by section_number if provided
            if section_number and s['section_number'] != section_number:
                continue
            # If needed, implement semester-based filtering for sections here
            filtered_sections.append(s)

        return render_template('search_results.html', results=filtered_sections, filter_type='section')

    # GOAL FILTER
    elif filter_type == 'goal':
        goal_code = request.args.get('goal_code', '').strip()
        all_goals_data = get_all_goals()  # Returns a list of dicts for all goals
        
        filtered_goals = []
        for g in all_goals_data:
            # Filter by goal_code if provided
            if goal_code and goal_code.lower() not in g['code'].lower():
                continue
            filtered_goals.append(g)

        return render_template('search_results.html', results=filtered_goals, filter_type='goal')

    # EVALUATION FILTER
    elif filter_type == 'evaluation':
        evaluation_method = request.args.get('evaluation_method', '').strip()
        all_evaluations_data = get_all_evaluations()  # Returns a list of dicts for evaluations
        
        filtered_evaluations = []
        for e in all_evaluations_data:
            # Filter by evaluation_method if provided
            if evaluation_method and evaluation_method.lower() not in (e['evaluation_method'] or '').lower():
                continue
            filtered_evaluations.append(e)

        return render_template('search_results.html', results=filtered_evaluations, filter_type='evaluation')

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

@app.route('/degree_courses/<int:degree_id>', methods=['GET'])
def degree_courses_route(degree_id):
    try:
        courses = get_degree_courses(degree_id)
        degree = get_degree(degree_id)
        
        if not degree:
            flash('Degree not found', 'error')
            return redirect(url_for('index'))
            
        print(f"Found {len(courses)} courses for degree {degree_id}")  # Debug log
        return render_template('degree_courses.html', 
                             courses=courses, 
                             degree=degree)
                             
    except Exception as e:
        print(f"Error in degree_courses_route: {str(e)}")  # Debug log
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))
    
@app.route('/select_degree/<string:query_type>')
def select_degree_route(query_type):
    degrees = get_degrees()
    return render_template('select_degree.html', 
                         degrees=degrees,
                         query_type=query_type)

# Update routes.py
@app.route('/degree_sections/<int:degree_id>', methods=['GET'])
def degree_sections_route(degree_id):
    try:
        # Get date range parameters with defaults
        current_year = datetime.now().year
        from_semester = request.args.get('from_semester', 'Spring')
        from_year = int(request.args.get('from_year', current_year))
        to_semester = request.args.get('to_semester', 'Fall')
        to_year = int(request.args.get('to_year', current_year))

        # Validate degree exists
        degree = get_degree(degree_id)
        if not degree:
            flash('Degree not found', 'error')
            return redirect(url_for('index'))

        # Get sections within date range
        sections = get_degree_sections(
            degree_id, 
            from_semester, from_year,
            to_semester, to_year
        )

        # Return template with all necessary data
        return render_template('degree_sections.html',
                             degree=degree,
                             sections=sections,
                             from_semester=from_semester,
                             from_year=from_year,
                             to_semester=to_semester,
                             to_year=to_year)

    except Exception as e:
        print(f"Error in degree_sections_route: {str(e)}")  # Debug log
        flash(str(e), 'error')
        return redirect(url_for('index'))
    
# routes.py
@app.route('/degree_goals/<int:degree_id>', methods=['GET'])
def degree_goals_route(degree_id):
    try:
        degree = get_degree(degree_id)
        if not degree:
            flash('Degree not found', 'error')
            return redirect(url_for('index'))
            
        goals = get_degree_goals(degree_id)
        return render_template('degree_goals.html',
                             goals=goals,
                             degree=degree)
    except Exception as e:
        print(f"Error: {str(e)}")
        flash(str(e), 'error')
        return redirect(url_for('index'))
    
# routes.py
@app.route('/goal_courses/<int:degree_id>', methods=['GET', 'POST'])
def goal_courses_route(degree_id):
    try:
        degree = get_degree(degree_id)
        if not degree:
            flash('Degree not found', 'error')
            return redirect(url_for('index'))
            
        goals = get_degree_goals(degree_id)
        
        if request.method == 'POST':
            selected_goals = request.form.getlist('goal_ids')
            if not selected_goals:
                flash('Please select at least one goal', 'error')
            else:
                goal_courses = get_courses_by_goals(selected_goals)
                return render_template('goal_courses.html',
                                     degree=degree,
                                     goals=goals,
                                     selected_goals=selected_goals,
                                     goal_courses=goal_courses)
                
        return render_template('goal_courses.html',
                             degree=degree,
                             goals=goals)
                             
    except Exception as e:
        print(f"Error: {str(e)}")
        flash(str(e), 'error')
        return redirect(url_for('index'))

@app.route('/evaluation_status', methods=['GET'])
def evaluation_status_route():
    semester = request.args.get('semester')
    year = request.args.get('year')
    percentage = request.args.get('percentage', type=float)
    
    if semester and year:
        try:
            sections = get_sections_evaluation_status(semester, year)
            filtered_sections = []
            
            for section in sections:
                grades_sum = (
                    section.get('grade_A', 0) + 
                    section.get('grade_B', 0) + 
                    section.get('grade_C', 0) + 
                    section.get('grade_F', 0)
                )
                
                if grades_sum > 0:
                    non_f = (
                        section.get('grade_A', 0) + 
                        section.get('grade_B', 0) + 
                        section.get('grade_C', 0)
                    )
                    section['pass_rate'] = round((non_f / grades_sum) * 100, 2)
                    
                    if percentage is None or section['pass_rate'] >= percentage:
                        filtered_sections.append(section)
                        
            return render_template('evaluation_status.html',
                                sections=filtered_sections,
                                semester=semester,
                                year=year,
                                percentage=percentage)
                                
        except Exception as e:
            flash(str(e), 'error')
            
    return render_template('evaluation_status.html')

@app.route('/get_goals_for_course/<int:course_id>', methods=['GET'])
def get_goals_for_course_route(course_id):
    try:
        goals = get_goals_for_course(course_id)
        if not goals:
            return jsonify({'message': 'No goals found for this course'}), 404
        return jsonify(goals)
    except Exception as e:
        print(f"Error in route for course {course_id}: {e}")
        return jsonify({'error': str(e)}), 500

