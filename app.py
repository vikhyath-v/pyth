from flask import Flask,session, render_template, request, redirect, url_for, flash
import sqlite3
import re
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO
import os



app = Flask(__name__)
app.secret_key = 'your_secret_key'



# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Drop the existing table if it exists (This will delete all current data)

    
    # Create a new table with the profile_image column
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL UNIQUE,
                  email TEXT NOT NULL UNIQUE,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Call this function to recreate the table
init_db()

global lcart 
lcart = []

# Separate products dictionary with imgname
products = {
 "1": {"name": "Osaka Sweatshirt", "price": 1999,"imgname": "biegesweat.jpg","category":"sweatshirt","gender":"male"},
  "7": {"name": "Pink top", "price": 999,"imgname": "pinktop.jpg","category":"top","gender":"female"},
      "13":{"name": "Black Jeans", "price": 999,"imgname": "blackjean.jpg","category":"jeans","gender":"male"},
        "11":{"name": "Green POLO tee", "price": 999,"imgname": "greenpolo.jpg","category":"tee","gender":"male"}
}

view_product ={
    "1": {"name": "Osaka Sweatshirt", "price": 1999,"imgname": "biegesweat.jpg","category":"sweatshirt","gender":"male"},
    "2": {"name": "white Sweatshirt", "price": 999,"imgname": "whitesweat.jpg","category":"sweatshirt","gender":"male"},
    "3": {"name": "Grey Sweatshirt", "price": 999,"imgname": "greysweatwom.jpg","category":"sweatshirt","gender":"female"},
    "4": {"name": "White Sweatshirt", "price": 999,"imgname": "whitesweatwom.jpg","category":"sweatshirt","gender":"female"},
    "5": {"name": "Maroon printed tee", "price": 999,"imgname": "maroontee.jpg","category":"tee","gender":"male"},
    "6": {"name": "Blue printed tee", "price": 999,"imgname": "blue_ov.jpg","category":"sweatshirt","gender":"male"},
    "7": {"name": "Pink top", "price": 999,"imgname": "pinktop.jpg","category":"top","gender":"female"},
    "8":{"name": "Floral top", "price": 999,"imgname": "floraltop.jpg","category":"top","gender":"female"},
    "9":{"name": "Yellow top", "price": 999,"imgname": "yellowtop.jpg","category":"top","gender":"female"},
    "10":{"name": "Pink POLO tee", "price": 999,"imgname": "pinkpolo.jpg","category":"tee","gender":"male"},
    "11":{"name": "Green POLO tee", "price": 999,"imgname": "greenpolo.jpg","category":"tee","gender":"male"},
    "12":{"name": "Grey POLO tee", "price": 999,"imgname": "greypolo.jpg","category":"tee","gender":"male"},
    "13":{"name": "Black Jeans", "price": 999,"imgname": "blackjean.jpg","category":"jeans","gender":"male"},
    "14":{"name": "BLue Jeans", "price": 999,"imgname": "bluejean.jpg","category":"jeans","gender":"male"},
    "15":{"name": "Brownish Jeans", "price": 999,"imgname": "brownjean.jpg","category":"jeans","gender":"male"},
    "16":{"name": "Low jeans ", "price": 999,"imgname": "lowjeanwom.jpg","category":"jeans","gender":"male"},
    "17":{"name": "Denim Jacket", "price": 999,"imgname": "denimjack.jpg","category":"jacket","gender":"female"},
    
    
    
    
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

# Signup route

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
            # Check if the username or email already exists
            existing_user = c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
            
            if existing_user:
                flash("Username or email already exists. Please login instead.", "error")
                return redirect(url_for('login'))  # Redirect to login page if user exists
            
            try:
                # Insert new user into the database
                c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                          (username, email, password))
                conn.commit()
                flash("Signup successful! Please login.", "success")
                return redirect(url_for('login'))  # Redirect to login page after signup
            except Exception as e:
                flash("Error saving user: {}".format(e), "error")
                conn.rollback()  # Rollback if there's an error
            finally:
                conn.close()
        else:
            for error in errors:
                flash(error, "error")

    return render_template('signup.html')

# Profile route to display user information
@app.route('/profile')
def profile():
    # Retrieve the username from session
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user_data = c.execute('SELECT username, email, profile_image FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user_data:
        profile_image = None
        if user_data[2]:
            profile_image = base64.b64encode(user_data[2]).decode('utf-8')  # Convert image to base64

        return render_template('profile.html', 
                               username=user_data[0], 
                               email=user_data[1], 
                               profile_image=profile_image)
    else:
        flash("User not found", "error")
        return redirect(url_for('login'))


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from session
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Attempting to log in with username: {username} and password: {password}")  # Debugging output

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # Fetch user data based on the provided username
        user = c.execute('SELECT username, password FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        # Debugging output for user retrieval
        print(f"Fetched user: {user}")  # Should show either a tuple (username, hashed_password) or None

        # Validate user credentials
        if user and user[1] == password:  # Compare password with user[1]
            # Store username in the session
            session['username'] = user[0]
            flash("Login successful!", "success")
            
            # Redirect to home page after successful login
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")
        
    return render_template('login.html')




@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html',products=products)
    else:
        return redirect(url_for('login'))
 
    
@app.route('/view_products')
def view_products():
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'default')

    # Initialize products with view_product
    products = view_product

    # Filter products by category if specified
    if category:
        products = {k: v for k, v in products.items() if v['category'] == category}

    return render_template('view_products.html', view_product=products)


@app.route('/product_page/<product_id>')
def product_page(product_id):
    product = products.get(product_id) or view_product.get(product_id)
    if product:
        return render_template('product_page.html', product=product, product_id=product_id)
    else:
        flash("Product not found.", "error")
        return redirect(url_for('home'))



@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = products.get(product_id) or view_product.get(product_id)
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


@app.route('/increase_quantity/<product_id>', methods=['POST'])
def increase_quantity(product_id):
    # Find the product in the cart
    for item in lcart:
        if item['id'] == product_id:
            if item['quantity'] >= 1:
                item['quantity'] += 1
                flash(f"Added {item['name']} quantity.", "success")
            else:
                # Optionally, remove the item if the quantity reaches 1
                lcart.remove(item)
                flash(f"Added {item['name']} from the cart.", "info")
            break
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

@app.route('/checkout/<product_id>', methods=['GET', 'POST'])
def checkout(product_id):
    product = products.get(product_id) or view_product.get(product_id)
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        if payment_method == 'card':
            card_number = request.form.get('card_number')
            expiry_date = request.form.get('expiry_date')
            # Process card payment
        elif payment_method == 'upi':
            upi_id = request.form.get('upi_id')
            # Process UPI payment
        # Redirect to order confirmation after processing
    return render_template('checkout.html', product=product,product_id=product_id)
   


@app.route('/order_confirmation')
def order_confirmation():
  
    delivery_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    return render_template('order_confirmation.html', delivery_date=delivery_date)


if __name__ == "__main__":
    app.run(debug=True, port=5002)