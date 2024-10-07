from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

cart = {}
shirts = {
    "1": "Levi Black T-Shirt",
    "2": "H&M Nirvana Themed T-Shirt",
    "3": "Deadpool and Wolverine "
}

@app.route('/')
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
