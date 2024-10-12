from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
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
            if user.approved:  # Check if the user is approved
                login_user(user)
                flash('Login successful', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.index'))  # Redirect to 'next' or index page after login
            else:
                flash('Your account is not approved yet.', 'danger')
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

# Define the form here
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

@auth.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Assuming you have a User model with an 'approved' field to mark pending approval
        user = User(username=form.username.data, email=form.email.data, password=form.password.data, approved=False)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created and is awaiting approval.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

# Route to view pending users, accessible only to super admins
@auth.route("/admin/approve_users")
@role_required('super_admin')  # Only super admins can access this route
def approve_users():
    pending_users = User.query.filter_by(approved=False).all()  # Get all unapproved users
    return render_template('approve_users.html', users=pending_users)

# Route to approve a user
@auth.route("/admin/approve/<int:user_id>")
@role_required('super_admin')  # Only super admins can approve
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.approved:
        flash(f'{user.username} is already approved.', 'info')
    else:
        user.approved = True
        db.session.commit()
        flash(f'{user.username} has been approved.', 'success')
    return redirect(url_for('auth.approve_users'))

