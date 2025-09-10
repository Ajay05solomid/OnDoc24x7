import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- Base Directory Setup ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# ---------------- Flask App Initialization ----------------
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = "your_secret_key"  # Apna strong secret key set karo

# ---------------- Database Helper Function ----------------
def get_db_connection():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'users.db'))
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- Home Route ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- Appointment Route ----------------
@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'username' not in session:
        flash("Please login to book an appointment.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        doctor = request.form['doctor']
        date = request.form['date']
        time_slot = request.form['time_slot']

        conn = sqlite3.connect(os.path.join(BASE_DIR, "users.db"))
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO appointments (name, email, doctor, date, time_slot) VALUES (?, ?, ?, ?, ?)",
            (name, email, doctor, date, time_slot)
        )
        conn.commit()
        conn.close()

        flash("Appointment booked successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template("appointment.html")

# ---------------- My Appointments Route ----------------
@app.route('/my_appointments')
def my_appointments():
    if 'username' not in session:
        flash("Please login to view your appointments.", "warning")
        return redirect(url_for('login'))

    conn = sqlite3.connect(os.path.join(BASE_DIR, "users.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT id, doctor, date, time_slot FROM appointments WHERE username = ?", (session['username'],))
    appointments = cursor.fetchall()
    conn.close()

    return render_template("my_appointments.html", appointments=appointments)

# ---------------- Signup Route ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE,
                            email TEXT UNIQUE,
                            password TEXT)''')
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                      (username, email, hashed_password))
            conn.commit()
            conn.close()

            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash("Username or Email already exists.", "danger")
            return redirect(url_for('signup'))

    return render_template('signup.html')

# ---------------- Login Route ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------------- Register Route ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except:
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template("register.html")

# ---------------- Dashboard Route ----------------
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        flash("Please login first.", "warning")
        return redirect(url_for('login'))

# ---------------- Symptom Prediction Route ----------------
@app.route('/symptom')
def symptom():
    if 'username' not in session:
        flash("Please login first to predict disease.", "warning")
        return redirect(url_for('login'))
    return render_template('symptom_input.html')

# ---------------- Logout Route ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)
