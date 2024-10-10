from flask import Flask,session, render_template, request, redirect, url_for, flash
import sqlite3
import re
import uuid
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

global lcart 
lcart = []

# Separate products dictionary with imgname
products = {
   "1": {"name": "Denim Jacket", "price": 999, "imgname": "denim jack.jpeg"},
   "2": {"name": "Blue Oversize Tee", "price": 1299, "imgname" : "blue_ov.jpeg"}
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
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                          (username, email, password))
                conn.commit()
                flash("Signup successful!", "success")
                return redirect(url_for('home'))
            except sqlite3.IntegrityError:
                flash("Username or email already exists. Please try again.", "error")
            finally:
                conn.close()
        else:
            for error in errors:
                flash(error, "error")
    
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html', products=products)

@app.route('/view_products')
def view_products():
    return render_template('view_products.html', products=products)

@app.route('/product_page/<product_id>')
def product_page(product_id):
    product = products.get(product_id)
    if product:
        return render_template('product_page.html', product=product, product_id=product_id)
    else:
        flash("Product not found.", "error")
        return redirect(url_for('home'))

@app.route('/buy_now/<product_id>', methods=['POST'])
def buy_now(product_id):
    product = products.get(product_id)
    if product:
        message = f"You have purchased {product['name']} for ₹{product['price']}."
        flash(message)  # This sets the flash message
        return redirect(url_for('product_page', product_id=product_id, success=message))  # Redirect to the product page
    else:
        flash("Product not found.", "error")
        return redirect(url_for('product_page'))  # Or redirect to a valid route

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = products.get(product_id)
    if product:
        # Check if the product is already in the cart
        for cart_item in lcart:
            if cart_item['id'] == product_id:
                # If the product is already in the cart, increment its quantity
                cart_item['quantity'] += 1
                flash(f"Updated {product['name']} quantity in your cart.", "success")
                return redirect(url_for('product_page', product_id=product_id))
        
        # If the product is not in the cart, add it with a new unique ID
        unique_cart_item_id = str(uuid.uuid4())
        lcart.append({
            'cart_item_id': unique_cart_item_id,  # Unique ID for this cart item
            'id': product_id,  # Product ID remains the same for the product itself
            'name': product['name'],
            'price': product['price'],
            'imgname': product['imgname'],
            'quantity': 1  # Each new addition starts with a quantity of 1
        })
        
        flash(f"You have added {product['name']} to your cart.", "success")
        return redirect(url_for('product_page', product_id=product_id))
    else:
        flash("Product not found.", "error")
        return redirect(url_for('view_products'))

@app.route('/view_cart')
def view_cart():  
    global cart
    if lcart:  # Check if lcart (global cart list) has any items
        cart = lcart
        total_amount = sum(item['price'] * item['quantity'] for item in cart)
        return render_template('view_cart.html', cart=cart, total_amount=total_amount)
    else:
        flash("Your cart is empty.", "info")
        return render_template('view_cart.html')





@app.route('/popcart', methods=['POST'])
def popcart():
    item_to_remove = request.form.get('item')
    if item_to_remove in cart:
        removed_item = cart.pop(item_to_remove)
        flash(f"{removed_item['name']} removed from cart.", "success")
    else:
        flash("Invalid item number. Please try again.", "error")
    return redirect(url_for('view_cart'))


@app.route('/reduce_quantity/<product_id>', methods=['POST'])
def reduce_quantity(product_id):
    # Find the product in the cart
    for item in lcart:
        if item['id'] == product_id:
            if item['quantity'] > 1:
                item['quantity'] -= 1
                flash(f"Reduced {item['name']} quantity.", "success")
            else:
                # Optionally, remove the item if the quantity reaches 1
                lcart.remove(item)
                flash(f"Removed {item['name']} from the cart.", "info")
            break
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    # Find the product in the cart and remove it
    for item in lcart:
        if item['id'] == product_id:
            lcart.remove(item)
            flash(f"Removed {item['name']} from your cart.", "info")
            break
    return redirect(url_for('view_cart'))


if __name__ == "__main__":
    app.run(debug=True, port=5002)
