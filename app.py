from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'hw13.db'

# Utility to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect('/login')
    
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()
    conn.close()
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if 'logged_in' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)', 
                         (first_name, last_name))
            conn.commit()
            return redirect('/dashboard')
        except Exception as e:
            flash('Error adding student')
        finally:
            conn.close()
    
    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if 'logged_in' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)', 
                         (subject, num_questions, quiz_date))
            conn.commit()
            return redirect('/dashboard')
        except Exception as e:
            flash('Error adding quiz')
        finally:
            conn.close()
    
    return render_template('add_quiz.html')

@app.route('/student/<int:student_id>')
def view_student_results(student_id):
    if 'logged_in' not in session:
        return redirect('/login')
    
    conn = get_db_connection()
    results = conn.execute(
        '''SELECT quizzes.subject, results.score 
           FROM results 
           JOIN quizzes ON results.quiz_id = quizzes.id 
           WHERE results.student_id = ?''', 
        (student_id,)
    ).fetchall()
    conn.close()
    
    return render_template('student_results.html', results=results)

@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if 'logged_in' not in session:
        return redirect('/login')
    
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        try:
            conn.execute('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)', 
                         (student_id, quiz_id, score))
            conn.commit()
            return redirect('/dashboard')
        except Exception as e:
            flash('Error adding result')
        finally:
            conn.close()
    
    conn.close()
    return render_template('add_result.html', students=students, quizzes=quizzes)

if __name__ == '__main__':
    app.run(debug=True)
