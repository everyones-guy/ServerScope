import flask
from flask_mail import Message
from . import mail

def notify_admins_of_new_user(user):
    admins = User.query.filter_by(is_super_admin=True).all()
    for admin in admins:
        msg = Message('New User Registration', sender='noreply@example.com', recipients=[admin.email])
        msg.body = f"User {user.username} has registered and needs approval."
        mail.send(msg)

