from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import sqlite3

app = Flask(__name__)
app.secret_key = 'ma_clee_de_securite'

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT,
                    classe TEXT
                )''')

    c.execute(''' CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )''')

    c.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not c.fetchone():
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))
    conn.commit()
    conn.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Si on soumet le formulaire
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username  # Stocker le nom dans la session
            return redirect(url_for('index'))  # Redirige vers la page principale
        else:
            return render_template('login.html', error='Identifiants incorrects')

    return render_template('login.html')  # Si on accède sans POST


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))  # Redirection si pas connecté
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@login_required
def index():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        classe = request.form['classe']

        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute('INSERT INTO students (name, phone, email, classe) VALUES (?, ?, ?, ?)', 
                  (name, phone, email, classe))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        classe = request.form['classe']

        c.execute('UPDATE students SET name=?, phone=?, email=?, classe=? WHERE id=?',
                  (name, phone, email, classe, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        c.execute('SELECT * FROM students WHERE id=?', (id,))
        student = c.fetchone()
        conn.close()
        return render_template('edit.html', student=student)

@app.route('/delete/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('DELETE FROM students WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user', None)  # Supprime l'utilisateur de la session
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run( host='0.0.0.0', port = 5000, debug=True)
