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
        goal_statuses = {}
        existing_data = {}
        other_degrees = get_degrees()  # Fetch all degrees for duplication

        if semester and instructor_id:
            sections = get_instructor_sections(instructor_id, semester, year)

        if section_id:
            goals = get_section_goals(section_id)
            for goal in goals:
                status = get_goal_completion_status(section_id, goal['goal_id'])
                goal_statuses[goal['goal_id']] = status

                eval_data = get_existing_evaluation(section_id, goal['goal_id'])
                if eval_data:
                    existing_data[goal['goal_id']] = eval_data

        return render_template(
            'add_evaluation.html',
            sections=sections,
            goals=goals,
            goal_statuses=goal_statuses,
            existing_data=existing_data,
            semester=semester,
            instructor_id=instructor_id,
            section_id=section_id,
            other_degrees=other_degrees  # Pass the degrees to the template
        )

    elif request.method == 'POST':
        try:
            section_id = request.form.get('section_id')
            goal_id = request.form.get('goal_id')
            save_as_draft = request.form.get('save_as_draft') == 'true'

            data = {
                'evaluation_method': request.form.get('evaluation_method'),
                'grade_A': int(request.form.get('num_a', '0')),
                'grade_B': int(request.form.get('num_b', '0')),
                'grade_C': int(request.form.get('num_c', '0')),
                'grade_F': int(request.form.get('num_f', '0')),
                'improvement_suggestion': request.form.get('improvement', ''),
            }

            add_or_update_evaluation(
                section_id=section_id,
                goal_id=goal_id,
                evaluation_method=data['evaluation_method'],
                num_a=data['grade_A'],
                num_b=data['grade_B'],
                num_c=data['grade_C'],
                num_f=data['grade_F'],
                improvement_notes=data['improvement_suggestion'],
            )

            duplicate_to_degrees = request.form.getlist('duplicate_to_degrees')
            if duplicate_to_degrees:
                for degree_id in duplicate_to_degrees:
                    duplicate_evaluation(goal_id, degree_id, section_id)

            if save_as_draft:
                flash('Evaluation saved as draft', 'success')
            else:
                flash('Evaluation completed successfully', 'success')
                return redirect(url_for('index'))

        except ValueError as e:
            flash(str(e), 'error')
            return redirect(request.url)
        except Exception as e:
            flash('Error saving evaluation', 'error')
            print(f"Error: {str(e)}")
            return redirect(request.url)

    flash('Invalid request', 'error')
    return redirect(url_for('index'))

        
from flask import request

@app.route('/search_route', methods=['GET'])
def search_route():
    filter_type = request.args.get('filter_type', '')

    if filter_type == 'degree':
        # We assume we have a function to get all degrees: get_degrees()
        # If no dedicated "get" method for searching exists, we implement filtering here.
        degree_name = request.args.get('degree_name', '').strip()
        all_degrees = get_degrees()  # returns a list of degrees, each presumably dict-like with 'name' key
        # Filter by name if provided
        filtered_degrees = []
        if degree_name:
            filtered_degrees = [d for d in all_degrees if degree_name.lower() in d['name'].lower()]
        else:
            filtered_degrees = all_degrees

        # Render your results or return JSON
        return render_template('search_results.html', results=filtered_degrees, filter_type='degree')

    elif filter_type == 'course':
        # Implement or call a "get_courses" function. If not implemented, write it.
        # Let's assume we have a function get_courses() that returns all courses.
        course_number = request.args.get('course_number', '').strip()
        from_semester = request.args.get('from_semester_course', '').strip()
        to_semester = request.args.get('to_semester_course', '').strip()

        # Hypothetical: get_courses() returns all courses. If not, implement get_courses().
        all_courses = get_all_courses()  
        # Now filter them based on the provided parameters
        filtered_courses = []
        for c in all_courses:
            # Assume each course has 'course_number', 'semester', etc.
            # If semester details are tracked differently, adjust filtering accordingly.
            if course_number and course_number.lower() not in c['course_number'].lower():
                continue
            # If we have semester info per course, you'd filter by date range.
            # Since specifics are not given, assume these filters are optional.
            # If "from_semester" and "to_semester" represent some comparable values, filter accordingly.
            # For example, if we store semester as a string like "Fall 2023", we might need a proper comparison method.
            # For now, let's skip semester-range filtering, or assume a simplistic check.
            
            filtered_courses.append(c)

        return render_template('search_results.html', results=filtered_courses, filter_type='course')

    elif filter_type == 'instructor':
        instructor_id = request.args.get('instructor_id', '').strip()
        from_semester = request.args.get('from_semester_instructor', '').strip()
        to_semester = request.args.get('to_semester_instructor', '').strip()

        # Implement a get_instructors() function if not available or filter from get_all_instructors()
        all_instructors = get_all_instructors()
        filtered_instructors = []
        for i in all_instructors:
            # Assume each instructor dict has 'id' and possibly associated sections/semesters.
            if instructor_id and instructor_id != i['id']:
                continue
            # Filtering by semester range would require instructor assignment data.
            # If not available, skip or implement as needed.
            filtered_instructors.append(i)

        return render_template('search_results.html', results=filtered_instructors, filter_type='instructor')

    elif filter_type == 'section':
        section_number = request.args.get('section_number', '').strip()
        from_semester = request.args.get('from_semester_section', '').strip()
        to_semester = request.args.get('to_semester_section', '').strip()

        # Assume a get_all_sections() function exists or implement it if it doesn't.
        all_sections = get_all_sections()  # You need to implement this in models if it doesn't exist.
        filtered_sections = []
        for s in all_sections:
            # Assume each section has 'section_number' and 'semester'.
            if section_number and section_number != s['section_number']:
                continue
            # Semester filtering logic can be added if we have structured semester data.
            filtered_sections.append(s)

        return render_template('search_results.html', results=filtered_sections, filter_type='section')

    elif filter_type == 'goal':
        goal_code = request.args.get('goal_code', '').strip()

        # Assume a get_all_goals() function exists. We have it from the imports.
        all_goals = get_all_goals()
        filtered_goals = []
        for g in all_goals:
            if goal_code and goal_code.lower() not in g['code'].lower():
                continue
            filtered_goals.append(g)

        return render_template('search_results.html', results=filtered_goals, filter_type='goal')

    elif filter_type == 'evaluation':
        evaluation_method = request.args.get('evaluation_method', '').strip()

        # If no get method for evaluations, implement one.
        # Let's assume we have get_all_evaluations(). If not, create it.
        all_evaluations = get_all_evaluations()  # You need to implement this in models if not existing.
        filtered_evaluations = []
        for e in all_evaluations:
            # Assume each evaluation has 'evaluation_method' field.
            if evaluation_method and evaluation_method.lower() not in e['evaluation_method'].lower():
                continue
            filtered_evaluations.append(e)

        return render_template('search_results.html', results=filtered_evaluations, filter_type='evaluation')

    else:
        # If no filter_type or unknown filter_type is selected.
        return "No valid filter type selected."

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