from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import User
from app import login_manager  # Import the login_manager from your app's __init__.py
from functools import wraps

auth = Blueprint('auth', __name__)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) if user_id else None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))  # Redirect to 'next' or index page after login
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('main.index'))

# Decorator for role-based access control
def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator
