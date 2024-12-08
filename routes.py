from flask import render_template, request, redirect, url_for, flash
from app import app
from models import add_degree, add_course, add_instructor, add_section, add_goal, associate_course_goal, get_degrees, get_all_courses, get_all_instructors, get_degree, get_courses_by_number, get_instructors_by_id, get_sections_by_number, get_goals_by_code, get_evaluations_by_method


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_degree', methods=['GET', 'POST'])
def add_degree_route():
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        add_degree(name, level)
        return redirect(url_for('index'))
    return render_template('add_degree.html')

@app.route('/add_course', methods=['GET', 'POST'])
def add_course_route():
    degrees = get_degrees()
    if request.method == 'POST':
        course_number = request.form['course_number']
        name = request.form['name']
        degree_ids = request.form.getlist('degree_ids')
        try:
            add_course(course_number, name, degree_ids)
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e))
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

            if not all([course_id, section_number, semester, instructor_id, students_enrolled]):
                raise ValueError("All fields are required")
                
            add_section(course_id, section_number, semester, 
                       instructor_id, students_enrolled)
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
    if request.method == 'POST':
        course_id = request.form['course_id']
        goal_id = request.form['goal_id']
        associate_course_goal(course_id, goal_id)
        return redirect(url_for('index'))
    return render_template('associate_course_goal.html')

@app.route('/add_evaluation', methods=['GET', 'POST'])
def add_evaluation_route():
    print("add_evaluation_route")
#     if request.method == 'GET':
#         # Get parameters for filtering
#         semester = request.args.get('semester')
#         year = request.args.get('year')
#         instructor_id = request.args.get('instructor_id')
        
#         # Get sections taught by instructor in semester
#         if semester and year and instructor_id:
#             sections = get_instructor_sections(instructor_id, semester, year)
#         else:
#             sections = []
            
#         return render_template('add_evaluation.html',
#                              sections=sections,
#                              semester=semester,
#                              year=year,
#                              instructor_id=instructor_id)
                             
#     elif request.method == 'POST':
#         try:
#             section_id = request.form.get('section_id')
#             goal_id = request.form.get('goal_id')
#             evaluation_method = request.form.get('evaluation_method')
#             num_a = int(request.form.get('num_a', 0))
#             num_b = int(request.form.get('num_b', 0))
#             num_c = int(request.form.get('num_c', 0))
#             num_f = int(request.form.get('num_f', 0))
#             improvement = request.form.get('improvement', '')

#             # Validate required fields
#             if not all([section_id, goal_id, evaluation_method]):
#                 raise ValueError("Section, goal and evaluation method are required")

#             # Validate grade counts are non-negative
#             if any(num < 0 for num in [num_a, num_b, num_c, num_f]):
#                 raise ValueError("Grade counts must be non-negative")

#             add_evaluation(
#                 section_id=section_id,
#                 goal_id=goal_id,
#                 evaluation_method=evaluation_method,
#                 num_a=num_a,
#                 num_b=num_b,
#                 num_c=num_c,
#                 num_f=num_f,
#                 improvement_suggestion=improvement
#             )

#             flash('Evaluation added successfully', 'success')
#             return redirect(url_for('add_evaluation_route', 
#                                   semester=request.form.get('semester'),
#                                   year=request.form.get('year'),
#                                   instructor_id=request.form.get('instructor_id')))

#         except ValueError as e:
#             flash(str(e), 'error')
#             return redirect(request.url)
#         except Exception as e:
#             flash('Error adding evaluation', 'error')
#             return redirect(request.url)
        
@app.route('/search_route', methods=['GET', 'POST'])
def search_route():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        search_type = request.form.get('filter_type')
        search_query = request.form.get('search_query')
        
        if search_type == 'degree':
            degree_name = request.form.get('degree_name')
            results = get_degree(degree_name)
        elif search_type == 'course':
            course_number = request.form.get('course_number')
            from_semester = request.form.get('from_semester_course')
            to_semester = request.form.get('to_semester_course')
            results = get_courses_by_number(course_number, from_semester, to_semester)
        elif search_type == 'instructor':
            instructor_id = request.form.get('instructor_id')
            from_semester = request.form.get('from_semester_instructor')
            to_semester = request.form.get('to_semester_instructor')
            results = get_instructors_by_id(instructor_id, from_semester, to_semester)
        elif search_type == 'section':
            section_number = request.form.get('section_number')
            from_semester = request.form.get('from_semester_section')
            to_semester = request.form.get('to_semester_section')
            results = get_sections_by_number(section_number, from_semester, to_semester)
        elif search_type == 'goal':
            goal_code = request.form.get('goal_code')
            results = get_goals_by_code(goal_code)
        elif search_type == 'evaluation':
            evaluation_method = request.form.get('evaluation_method')
            results = get_evaluations_by_method(evaluation_method)
        else:
            results = []
        
        return render_template('search_results.html', results=results, search_type=search_type)
    
    return render_template('search.html')
        