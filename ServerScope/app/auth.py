from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from functools import wraps
from app.models import User  # Assuming you have a User model in models.py

auth = Blueprint('auth', __name__)

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Use the User model to load user by ID

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Fetch the user from the database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # User exists and password matches, log them in
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))  # Redirect to the homepage after login
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))  # Reload the login page on failure
    
    # If GET request, display the login page
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('main.index'))  # Redirect to homepage after logout

def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator
