# auth.py

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import redirect, url_for, abort
from functools import wraps

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return current_user.query.get(int(user_id))

def login():
    # Your login logic goes here
    pass

def logout():
    logout_user()
    return redirect(url_for('main.index'))


def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator

