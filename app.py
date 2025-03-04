from flask import Flask, render_template, request, redirect, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'store.db'

# Database Connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize Database
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)''')
        db.commit()

@app.route('/')
def home():
    if 'user' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return render_template('store.html', products=products)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            session['user'] = username
            return redirect('/')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Username already exists. Please choose another."
    return render_template('register.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' in session:
        name = request.form['name']
        price = request.form['price']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        db.commit()
    return redirect('/')

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    if 'user' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        db.commit()
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0",port=5000, debug=True)
