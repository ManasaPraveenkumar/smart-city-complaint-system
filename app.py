from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret123'

# Upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Home
@app.route('/')
def home():
    return render_template('index.html')


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        if not name or not email or not password:
            return "All fields are required!"

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, role)
            )
            conn.commit()
        except:
            return "Email already exists!"

        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email or not password:
            return "All fields are required!"

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[4]

            if user[4] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password!")
    return render_template('login.html')


# USER DASHBOARD
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Total
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    # Pending
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = cursor.fetchone()[0]

    # In Progress
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='In Progress'")
    in_progress = cursor.fetchone()[0]

    # Resolved
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
    resolved = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved
    )


# ADMIN DASHBOARD
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# COMPLAINT SUBMISSION
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        location = request.form['location']

        if not title or not description or not category or not location:
            return "All fields are required!"

        file = request.files['image']
        filename = ""

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO complaints (user_id, title, description, category, location, image, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session.get('user_id'), title, description, category, location, filename, date))

        conn.commit()
        conn.close()

        return redirect(url_for('view_complaints'))

    return render_template('complaint.html')


# VIEW COMPLAINTS
@app.route('/view_complaints')
def view_complaints():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    conn.close()

    return render_template('view_complaints.html', complaints=complaints)


# UPDATE STATUS (ADMIN ONLY)
@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):

    if session.get('role') != 'admin':
        return "Access Denied!"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE complaints SET status=? WHERE id=?", (status, id))

    conn.commit()
    conn.close()

    return redirect(url_for('view_complaints'))


if __name__ == '__main__':
    app.run(debug=True)