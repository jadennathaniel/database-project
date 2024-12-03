from flask import render_template, request, redirect, url_for
from app import app, get_db_connection
from models import create_tables

@app.route('/')
def index():
    create_tables()
    return render_template('index.html')

@app.route('/add_degree', methods=['GET', 'POST'])
def add_degree():
    if request.method == 'POST':
        name = request.form['name']
        level = request.form['level']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Degree (name, level) VALUES (%s, %s)', (name, level))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_degree.html')

# Add more routes for other operations