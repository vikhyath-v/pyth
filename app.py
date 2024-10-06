from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure database (replace with your desired database URI)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Add basic validation (optional)
        # For example, check if username or email already exists

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        # Display success message
        signup_message = "Signup successful! You can now log in."
        return render_template('signup.html', signup_message=signup_message)

    return render_template('signup.html')

if __name__ == '__main__':
    # Create the database tables (uncomment if needed)
    # db.create_all()
    app.run(debug=True, port=5001)  # Use a non-conflicting port (e.g., 5001)