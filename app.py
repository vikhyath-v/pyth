from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL UNIQUE,
                  email TEXT NOT NULL UNIQUE,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

cart = {}
shirts = {
    "1": "Levi Black T-Shirt",
    "2": "H&M Nirvana Themed T-Shirt",
    "3": "Deadpool and Wolverine"
}

def validate_signup(username, email, password):
    errors = []
    
    # Username validation
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters long.")
    if not re.match("^[a-zA-Z0-9_]+$", username):
        errors.append("Username can only contain letters, numbers, and underscores.")
    
    # Email validation
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append("Please enter a valid email address.")
    
    # Password validation
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search("[a-z]", password) or not re.search("[A-Z]", password) or not re.search("[0-9]", password):
        errors.append("Password must contain at least one lowercase letter, one uppercase letter, and one digit.")
    
    return errors

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Validate input
        errors = validate_signup(username, email, password)
        
        if not errors:
            # Hash the password
            
            
            user_data = {
                'username': username,
                'email': email,
                'password': password
            }
            
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                          (user_data['username'], user_data['email'], user_data['password']))
                conn.commit()
                flash("Signup successful!", "success")
                return redirect(url_for('display_menu'))
            except sqlite3.IntegrityError:
                flash("Username or email already exists. Please try again.", "error")
            finally:
                conn.close()
        else:
            for error in errors:
                flash(error, "error")
    
    return render_template('signup.html')

@app.route('/menu')
def display_menu():
    return render_template('menu.html', cart=cart, shirts=shirts)

@app.route('/view_products')
def view_products():
    return render_template('view_products.html', shirts=shirts)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item = request.form.get('item')
    if item in shirts:
        cart[item] = shirts[item]
        flash(f"{shirts[item]} added to cart.", "success")
    else:
        flash("Invalid item number. Please try again.", "error")
    return redirect(url_for('display_menu'))

@app.route('/view_cart')
def view_cart():
    return render_template('view_cart.html', cart=cart)

@app.route('/popcart', methods=['POST'])
def popcart():
    item_to_remove = request.form.get('item')
    if item_to_remove in cart:
        removed_item = cart.pop(item_to_remove)
        flash(f"{removed_item} removed from cart.", "success")
    else:
        flash("Invalid item number. Please try again.", "error")
    return redirect(url_for('display_menu'))

if __name__ == "__main__":
    app.run(debug=True, port=5002)
