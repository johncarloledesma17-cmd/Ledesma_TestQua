import sys
import os

# Tell Python to look inside the 'db' folder for dbhelper.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db'))

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dbhelper import getrecord, addrecord

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_testing'

# --- THE FIX FOR BUG-01 (From your PDF) ---
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/')
def index():
    return redirect(url_for('login'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # TEST CASE F-03: Password mismatch
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('register'))

        # TEST CASE F-02: Duplicate email
        existing_user = getrecord('accounts', email=email)
        if len(existing_user) > 0:
            flash('Email already exists!', 'error')
            return redirect(url_for('register'))

        # TEST CASE F-01: Valid registration
        # Using addrecord from your dbhelper
        addrecord('accounts', email=email, full_name=full_name, password=password)
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Use your dbhelper to check the 'accounts' table
        user = getrecord('accounts', email=email, password=password)

        if len(user) > 0:
            # user[0][0] is email, user[0][1] is full_name
            session['user_email'] = user[0][0] 
            session['user_name'] = user[0][1] 
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', name=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)